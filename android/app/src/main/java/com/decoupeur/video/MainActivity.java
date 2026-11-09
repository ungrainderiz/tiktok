package com.decoupeur.video;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends Activity {

    private static final int REQ_PICK = 1;

    private Button pick, share;
    private EditText taille;
    private ProgressBar bar;
    private TextView journal;
    private ScrollView scroll;
    private volatile boolean busy;
    private final ArrayList<Uri> lastParts = new ArrayList<>();

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        buildUi();
        handle(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        handle(intent);
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private void buildUi() {
        int bg = Color.parseColor("#121212"), fg = Color.WHITE, accent = Color.parseColor("#FE2C55");
        getWindow().setStatusBarColor(bg);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(bg);
        root.setPadding(dp(20), dp(28), dp(20), dp(20));

        TextView titre = new TextView(this);
        titre.setText("Découpeur vidéo");
        titre.setTextColor(fg);
        titre.setTextSize(26);
        titre.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(titre);

        TextView sous = new TextView(this);
        sous.setText("Coupe une grosse vidéo en parties de taille maximale, sans perte de qualité.");
        sous.setTextColor(Color.parseColor("#AAAAAA"));
        sous.setTextSize(14);
        sous.setPadding(0, dp(4), 0, dp(18));
        root.addView(sous);

        LinearLayout ligne = new LinearLayout(this);
        ligne.setGravity(Gravity.CENTER_VERTICAL);
        TextView l1 = new TextView(this);
        l1.setText("Taille max d'une partie :  ");
        l1.setTextColor(fg);
        l1.setTextSize(16);
        ligne.addView(l1);
        taille = new EditText(this);
        taille.setText("30");
        taille.setTextColor(fg);
        taille.setTextSize(18);
        taille.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
        taille.setGravity(Gravity.CENTER);
        taille.setMinWidth(dp(64));
        ligne.addView(taille);
        TextView l2 = new TextView(this);
        l2.setText(" Mo");
        l2.setTextColor(fg);
        l2.setTextSize(16);
        ligne.addView(l2);
        root.addView(ligne);

        pick = bouton("Choisir une vidéo", accent);
        pick.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { choisir(); }
        });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(56));
        lp.topMargin = dp(18);
        root.addView(pick, lp);

        bar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        bar.setMax(1000);
        bar.getProgressDrawable().setTint(accent);
        LinearLayout.LayoutParams bp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(10));
        bp.topMargin = dp(18);
        root.addView(bar, bp);

        scroll = new ScrollView(this);
        journal = new TextView(this);
        journal.setTextColor(Color.parseColor("#DDDDDD"));
        journal.setTextSize(13);
        journal.setTypeface(Typeface.MONOSPACE);
        journal.setText("Astuce : depuis ta galerie, tu peux aussi « Partager » une vidéo "
                + "vers cette appli.\n\nLes parties sont enregistrées dans la galerie, "
                + "dossier Movies/Decoupeur.\n");
        scroll.addView(journal);
        LinearLayout.LayoutParams sp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f);
        sp.topMargin = dp(14);
        root.addView(scroll, sp);

        share = bouton("Partager les parties", Color.parseColor("#25F4EE"));
        share.setTextColor(Color.BLACK);
        share.setVisibility(View.GONE);
        share.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { partager(); }
        });
        LinearLayout.LayoutParams shp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(52));
        shp.topMargin = dp(10);
        root.addView(share, shp);

        setContentView(root);
    }

    private Button bouton(String texte, int couleur) {
        Button b = new Button(this);
        b.setText(texte);
        b.setAllCaps(false);
        b.setTextSize(17);
        b.setTypeface(Typeface.DEFAULT_BOLD);
        b.setTextColor(Color.WHITE);
        GradientDrawable d = new GradientDrawable();
        d.setColor(couleur);
        d.setCornerRadius(dp(14));
        b.setBackground(d);
        return b;
    }

    private void handle(Intent intent) {
        if (intent == null) return;
        Uri uri = null;
        if (Intent.ACTION_SEND.equals(intent.getAction())) {
            uri = intent.getParcelableExtra(Intent.EXTRA_STREAM);
        } else if (Intent.ACTION_VIEW.equals(intent.getAction())) {
            uri = intent.getData();
        }
        if (uri != null) demarrer(uri);
    }

    private void choisir() {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("video/*");
        startActivityForResult(i, REQ_PICK);
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == REQ_PICK && res == RESULT_OK && data != null && data.getData() != null) {
            demarrer(data.getData());
        }
    }

    private void log(final String msg) {
        runOnUiThread(new Runnable() {
            @Override public void run() {
                journal.append(msg + "\n");
                scroll.post(new Runnable() {
                    @Override public void run() { scroll.fullScroll(View.FOCUS_DOWN); }
                });
            }
        });
    }

    private void demarrer(final Uri uri) {
        if (busy) {
            log("Un découpage est déjà en cours, patiente…");
            return;
        }
        double mo;
        try {
            mo = Double.parseDouble(taille.getText().toString().replace(',', '.'));
        } catch (NumberFormatException e) {
            mo = 0;
        }
        if (mo < 1) {
            log("❌ Taille invalide.");
            return;
        }
        final long limite = (long) (mo * Splitter.MO);
        busy = true;
        pick.setEnabled(false);
        pick.setAlpha(0.5f);
        share.setVisibility(View.GONE);
        bar.setProgress(0);
        journal.setText("");
        lastParts.clear();
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        log("Garde l'appli ouverte pendant le découpage.\n");

        new Thread(new Runnable() {
            @Override public void run() {
                Splitter.Result r = null;
                try {
                    r = new Splitter(MainActivity.this, uri, limite, new Splitter.Listener() {
                        @Override public void log(String m) { MainActivity.this.log(m); }
                        @Override public void progress(final float f) {
                            runOnUiThread(new Runnable() {
                                @Override public void run() { bar.setProgress((int) (f * 1000)); }
                            });
                        }
                    }).run();
                    if (r.someTooBig) {
                        log("⚠ Certaines parties dépassent la limite : les images clés de "
                                + "cette vidéo sont trop espacées pour couper plus finement.");
                    }
                    log("\nTerminé ! " + r.parts.size()
                            + " parties dans la galerie (Movies/Decoupeur).");
                } catch (Throwable e) {
                    String m = e.getMessage();
                    if (e instanceof java.lang.reflect.InvocationTargetException && e.getCause() != null)
                        m = e.getCause().getMessage();
                    log("\n❌ Erreur : " + (m != null ? m : e.toString())
                            + "\n(Format conseillé : MP4 / MOV filmé avec un téléphone.)");
                }
                final List<Uri> parts = r != null ? r.parts : null;
                runOnUiThread(new Runnable() {
                    @Override public void run() {
                        busy = false;
                        pick.setEnabled(true);
                        pick.setAlpha(1f);
                        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                        if (parts != null && !parts.isEmpty()) {
                            lastParts.addAll(parts);
                            share.setVisibility(View.VISIBLE);
                        }
                    }
                });
            }
        }).start();
    }

    private void partager() {
        if (lastParts.isEmpty()) return;
        Intent i = new Intent(Intent.ACTION_SEND_MULTIPLE);
        i.setType("video/mp4");
        i.putParcelableArrayListExtra(Intent.EXTRA_STREAM, new ArrayList<>(lastParts));
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivity(Intent.createChooser(i, "Partager les parties"));
    }
}
