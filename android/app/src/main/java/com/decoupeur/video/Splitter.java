package com.decoupeur.video;

import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.media.MediaCodec;
import android.media.MediaExtractor;
import android.media.MediaFormat;
import android.media.MediaMuxer;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.MediaStore;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Method;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/**
 * Coupe une vidéo en parties de taille maximale donnée, sans réencodage
 * (MediaExtractor + MediaMuxer : on recopie les images telles quelles).
 * Les coupes se font sur des images clés pour que chaque partie soit lisible.
 */
public class Splitter {

    public interface Listener {
        void log(String message);
        void progress(float fraction);
    }

    public static class Result {
        public final List<Uri> parts = new ArrayList<>();
        public boolean someTooBig;
    }

    static final long MO = 1_000_000L;
    static final String DOSSIER = "Movies/Decoupeur";

    private final Context ctx;
    private final ContentResolver cr;
    private final Uri src;
    private final long limit;
    private final Listener l;

    public Splitter(Context ctx, Uri src, long limitBytes, Listener listener) {
        this.ctx = ctx;
        this.cr = ctx.getContentResolver();
        this.src = src;
        this.limit = limitBytes;
        this.l = listener;
    }

    // Liste compacte des échantillons (ordre du fichier)
    private int count;
    private int[] sTrack = new int[1 << 14];
    private long[] sTime = new long[1 << 14];
    private int[] sSize = new int[1 << 14];
    private boolean[] sKey = new boolean[1 << 14];

    private void add(int track, long time, int size, boolean key) {
        if (count == sTrack.length) {
            int n = count * 2;
            sTrack = Arrays.copyOf(sTrack, n);
            sTime = Arrays.copyOf(sTime, n);
            sSize = Arrays.copyOf(sSize, n);
            sKey = Arrays.copyOf(sKey, n);
        }
        sTrack[count] = track;
        sTime[count] = time;
        sSize[count] = size;
        sKey[count] = key;
        count++;
    }

    public Result run() throws Exception {
        String name = displayName();
        String base = name.replaceAll("\\.[^.]*$", "");
        long total = sourceSize();
        l.log(String.format(Locale.FRANCE, "Vidéo : %s (%.1f Mo)", name, total / (double) MO));

        Result res = new Result();
        if (total > 0 && total <= limit) {
            l.log("La vidéo fait déjà moins de la limite : copiée telle quelle.");
            InputStream in = cr.openInputStream(src);
            res.parts.add(publish(in, base + "_partie01.mp4"));
            l.progress(1f);
            return res;
        }

        // ---- Passe 1 : inventaire des échantillons (rapide, sans lire les données)
        l.log("Analyse de la vidéo…");
        MediaExtractor ex = new MediaExtractor();
        ex.setDataSource(ctx, src, null);
        int videoTrack = -1;
        List<Integer> tracks = new ArrayList<>();
        int rotation = 0;
        long duration = 0;
        for (int i = 0; i < ex.getTrackCount(); i++) {
            MediaFormat f = ex.getTrackFormat(i);
            String mime = f.getString(MediaFormat.KEY_MIME);
            if (mime == null) continue;
            if (mime.startsWith("video/") && videoTrack < 0) {
                videoTrack = i;
                if (f.containsKey("rotation-degrees")) rotation = f.getInteger("rotation-degrees");
            } else if (!mime.startsWith("audio/")) {
                continue;
            }
            if (f.containsKey(MediaFormat.KEY_DURATION))
                duration = Math.max(duration, f.getLong(MediaFormat.KEY_DURATION));
            tracks.add(i);
            ex.selectTrack(i);
        }
        if (videoTrack < 0) throw new Exception("Aucune piste vidéo dans ce fichier.");

        Method getSampleSize = MediaExtractor.class.getMethod("getSampleSize"); // API 28+
        int maxSample = 1 << 20;
        int t;
        while ((t = ex.getSampleTrackIndex()) >= 0) {
            long time = ex.getSampleTime();
            int size = (int) (long) (Long) getSampleSize.invoke(ex);
            boolean key = t == videoTrack
                    && (ex.getSampleFlags() & MediaExtractor.SAMPLE_FLAG_SYNC) != 0;
            add(t, time, size, key);
            if (size > maxSample) maxSample = size;
            if (duration > 0 && (count & 1023) == 0) l.progress(0.05f * time / duration);
            ex.advance();
        }
        ex.release();
        if (count == 0) throw new Exception("Impossible de lire le contenu de la vidéo.");

        // ---- Passe 2 : écriture des parties (avec nouvel essai si une partie déborde)
        double marge = 0.97;
        for (int essai = 0; ; essai++) {
            long budget = (long) (limit * marge) - 200_000;
            int[] cuts = plan(videoTrack, budget);
            boolean impossible = cuts[cuts.length - 1] < 0;
            if (impossible) cuts = Arrays.copyOf(cuts, cuts.length - 1);
            l.log("Découpage en " + (cuts.length + 1) + " parties…");

            Result r = write(base, tracks, videoTrack, rotation, duration, cuts, maxSample,
                    !impossible && essai < 5);
            if (r != null) {
                l.progress(1f);
                return r;
            }
            marge -= 0.04;
            l.log("Une partie dépasse légèrement, nouvel essai avec plus de marge…");
        }
    }

    /**
     * Renvoie les indices (dans la liste d'échantillons) des images clés où commence
     * chaque nouvelle partie. Si un intervalle entre deux images clés dépasse à lui seul
     * le budget, le dernier élément vaut -1.
     */
    private int[] plan(int videoTrack, long budget) {
        ArrayList<Integer> cuts = new ArrayList<>();
        long octets = 0;
        int lastKey = -1;
        long octetsAvant = 0;
        boolean first = true, tooBig = false;
        for (int i = 0; i < count; i++) {
            if (sTrack[i] == videoTrack && sKey[i]) {
                if (first) first = false;
                else { lastKey = i; octetsAvant = octets; }
            }
            if (octets + sSize[i] > budget) {
                if (lastKey >= 0) {
                    cuts.add(lastKey);
                    octets -= octetsAvant;
                    lastKey = -1;
                } else {
                    tooBig = true;
                }
            }
            octets += sSize[i];
        }
        int[] out = new int[cuts.size() + (tooBig ? 1 : 0)];
        for (int i = 0; i < cuts.size(); i++) out[i] = cuts.get(i);
        if (tooBig) out[out.length - 1] = -1;
        return out;
    }

    private static class Part {
        File file;
        MediaMuxer muxer;
        int[] trackMap;
    }

    /** Écrit les parties. Renvoie null (et nettoie) si une partie dépasse et qu'on peut réessayer. */
    private Result write(String base, List<Integer> tracks, int videoTrack, int rotation,
                         long duration, int[] cuts, int maxSample, boolean canRetry) throws Exception {
        int nParts = cuts.length + 1;
        long[] cutTime = new long[nParts];
        for (int k = 1; k < nParts; k++) cutTime[k] = sTime[cuts[k - 1]];

        MediaExtractor ex = new MediaExtractor();
        ex.setDataSource(ctx, src, null);
        for (int tr : tracks) ex.selectTrack(tr);

        Result res = new Result();
        Part[] parts = new Part[nParts];
        ByteBuffer buf = ByteBuffer.allocateDirect(maxSample + 1024);
        MediaCodec.BufferInfo info = new MediaCodec.BufferInfo();
        int vSeg = 0, aSeg = 0, i = 0, nextClose = 0;
        File cache = ctx.getCacheDir();
        try {
            int t;
            while ((t = ex.getSampleTrackIndex()) >= 0) {
                long time = ex.getSampleTime();
                int seg;
                if (t == videoTrack) {
                    // vidéo : on suit l'ordre du fichier, nouvelle partie à chaque image clé de coupe
                    while (vSeg + 1 < nParts && i >= cuts[vSeg]) vSeg++;
                    seg = vSeg;
                } else {
                    // audio : on suit l'horodatage
                    while (aSeg + 1 < nParts && time >= cutTime[aSeg + 1]) aSeg++;
                    seg = aSeg;
                }
                i++;

                if (seg < nextClose) { // retardataire d'une partie déjà fermée : ignoré
                    ex.advance();
                    continue;
                }
                if (parts[seg] == null) {
                    // une partie qui commence : on ferme celles qui sont terminées depuis longtemps
                    while (nextClose < seg - 1) {
                        if (!finish(parts, nextClose, base, res, canRetry)) return abort(parts, res);
                        nextClose++;
                    }
                    parts[seg] = open(ex, tracks, rotation, cache, seg);
                }

                long pts = time - cutTime[seg];
                if (pts >= 0) {
                    int size = ex.readSampleData(buf, 0);
                    if (size > 0) {
                        boolean key = t != videoTrack
                                || (ex.getSampleFlags() & MediaExtractor.SAMPLE_FLAG_SYNC) != 0;
                        info.set(0, size, pts, key ? MediaCodec.BUFFER_FLAG_KEY_FRAME : 0);
                        Part p = parts[seg];
                        p.muxer.writeSampleData(p.trackMap[t], buf, info);
                    }
                }
                if (duration > 0 && (i & 255) == 0)
                    l.progress(0.05f + 0.95f * Math.min(1f, time / (float) duration));
                ex.advance();
            }
            for (int k = nextClose; k < nParts; k++) {
                if (!finish(parts, k, base, res, canRetry)) return abort(parts, res);
            }
        } finally {
            ex.release();
        }
        return res;
    }

    private Part open(MediaExtractor ex, List<Integer> tracks, int rotation, File dir, int seg)
            throws Exception {
        Part p = new Part();
        p.file = new File(dir, "partie" + seg + ".mp4");
        p.muxer = new MediaMuxer(p.file.getAbsolutePath(), MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
        p.trackMap = new int[ex.getTrackCount()];
        for (int tr : tracks) p.trackMap[tr] = p.muxer.addTrack(ex.getTrackFormat(tr));
        if (rotation != 0) p.muxer.setOrientationHint(rotation);
        p.muxer.start();
        return p;
    }

    /** Termine la partie k, vérifie sa taille et la publie dans la galerie. */
    private boolean finish(Part[] parts, int k, String base, Result res, boolean canRetry)
            throws Exception {
        Part p = parts[k];
        if (p == null) return true;
        parts[k] = null;
        try {
            p.muxer.stop();
        } finally {
            p.muxer.release();
        }
        long size = p.file.length();
        if (size > limit) {
            if (canRetry) {
                p.file.delete();
                return false;
            }
            res.someTooBig = true;
        }
        String nom = String.format(Locale.ROOT, "%s_partie%02d.mp4", base, k + 1);
        res.parts.add(publish(new FileInputStream(p.file), nom));
        p.file.delete();
        l.log(String.format(Locale.FRANCE, "  ✔ %s : %.2f Mo", nom, size / (double) MO));
        return true;
    }

    private Result abort(Part[] parts, Result res) {
        for (Part p : parts) {
            if (p == null) continue;
            try { p.muxer.stop(); } catch (Exception ignored) { }
            p.muxer.release();
            p.file.delete();
        }
        for (Uri u : res.parts) {
            try { cr.delete(u, null, null); } catch (Exception ignored) { }
        }
        return null;
    }

    /** Copie un fichier dans la galerie (Films/Decoupeur). */
    private Uri publish(InputStream in, String displayName) throws Exception {
        ContentValues v = new ContentValues();
        v.put(MediaStore.MediaColumns.DISPLAY_NAME, displayName);
        v.put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4");
        v.put("relative_path", DOSSIER);   // MediaStore.MediaColumns.RELATIVE_PATH (API 29)
        v.put("is_pending", 1);            // MediaStore.MediaColumns.IS_PENDING (API 29)
        Uri uri = cr.insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, v);
        if (uri == null) throw new Exception("Impossible d'enregistrer dans la galerie.");
        try {
            OutputStream out = cr.openOutputStream(uri);
            try {
                byte[] b = new byte[1 << 16];
                int n;
                while ((n = in.read(b)) > 0) out.write(b, 0, n);
            } finally {
                out.close();
            }
        } catch (Exception e) {
            cr.delete(uri, null, null);
            throw e;
        } finally {
            in.close();
        }
        ContentValues done = new ContentValues();
        done.put("is_pending", 0);
        cr.update(uri, done, null, null);
        return uri;
    }

    private String displayName() {
        try {
            Cursor c = cr.query(src, new String[]{OpenableColumns.DISPLAY_NAME}, null, null, null);
            if (c != null) {
                try {
                    if (c.moveToFirst() && c.getString(0) != null) return c.getString(0);
                } finally {
                    c.close();
                }
            }
        } catch (Exception ignored) { }
        String last = src.getLastPathSegment();
        return last != null ? last.replaceAll(".*/", "") : "video.mp4";
    }

    private long sourceSize() {
        try {
            ParcelFileDescriptor pfd = cr.openFileDescriptor(src, "r");
            if (pfd != null) {
                long s = pfd.getStatSize();
                pfd.close();
                if (s > 0) return s;
            }
        } catch (Exception ignored) { }
        return -1;
    }
}
