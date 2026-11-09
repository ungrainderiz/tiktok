/*
 * Roster étendu : les champions des deux « générations » utilisées par l'affiche
 * « Anciens (2009-2010) vs Nouveaux (2013-2025) », avec leur année de sortie.
 *
 * Une ligne = id | nom | année | rôle | couleur | sort | type | ultime | type
 *   rôles : T tank, F combattant, A assassin, M mage, D tireur, S support
 *   types : n nuke, a aoe, s spin, d dash, t stun, x aoestun, h heal, e execute, r drain
 *
 * Les champions déjà décrits dans src/roster.js gardent leurs sorts ; on leur ajoute l'année.
 * Dans battle.config.js, `champions: { from: 2009, to: 2010 }` prend tous les champions
 * sortis entre ces deux années.
 */
(function (root) {
  const TABLE = `
alistar|Alistar|2009|T|#7a5c9e|Pulverize|x|Unbreakable Will|h
annie|Annie|2009|M|#e0533a|Disintegrate|n|Summon: Tibbers|x
ashe|Ashe|2009|D|#7fb8e6|Volley|a|Enchanted Crystal Arrow|t
fiddlesticks|Fiddlesticks|2009|M|#8a6a3a|Terrify|t|Crowstorm|s
jax|Jax|2009|F|#7a4fb0|Leap Strike|d|Grandmaster's Might|n
kayle|Kayle|2009
masteryi|Master Yi|2009|A|#d9c24a|Alpha Strike|a|Highlander|r
morgana|Morgana|2009
nunu|Nunu & Willump|2009|T|#7ec8e8|Consume|r|Absolute Zero|x
ryze|Ryze|2009|M|#3f7fd6|Overload|n|Realm Warp|a
sion|Sion|2009
sivir|Sivir|2009|D|#d9a441|Boomerang Blade|a|On The Hunt|n
soraka|Soraka|2009|S|#e8d36a|Starcall|a|Wish|h
teemo|Teemo|2009
tristana|Tristana|2009|D|#4f9fd6|Rocket Jump|d|Buster Shot|n
twistedfate|Twisted Fate|2009|M|#5a4fb0|Wild Cards|a|Destiny|d
warwick|Warwick|2009|F|#8a8a8a|Jaws of the Beast|r|Infinite Duress|d
singed|Singed|2009|T|#7fbf3f|Poison Trail|s|Insanity Potion|h
zilean|Zilean|2009|S|#d9b44a|Time Bomb|a|Chronoshift|h
evelynn|Evelynn|2009|A|#c04fa0|Hate Spike|n|Last Caress|e
twitch|Twitch|2009|D|#6f9a3a|Venom Cask|a|Spray and Pray|a
karthus|Karthus|2009|M|#5f6fb0|Lay Waste|a|Requiem|a
amumu|Amumu|2009|T|#9fbf8a|Bandage Toss|t|Curse of the Sad Mummy|x
chogath|Cho'Gath|2009|T|#7a4fa0|Rupture|x|Feast|e
anivia|Anivia|2009|M|#6fc0e8|Flash Frost|t|Glacial Storm|a
rammus|Rammus|2009|T|#b08a5a|Powerball|d|Soaring Slam|x
veigar|Veigar|2009|M|#6a3fa8|Baleful Strike|n|Primordial Burst|e
kassadin|Kassadin|2009|A|#7a5fc8|Null Sphere|n|Riftwalk|d
gangplank|Gangplank|2009|F|#c0603a|Parrrley|n|Cannon Barrage|a
taric|Taric|2009|S|#4fc8d8|Starlight's Touch|h|Cosmic Radiance|h
blitzcrank|Blitzcrank|2009|T|#d9b43a|Rocket Grab|t|Static Field|x
malphite|Malphite|2009
janna|Janna|2009|S|#9fd8e8|Howling Gale|x|Monsoon|h
tryndamere|Tryndamere|2009|F|#c04a4a|Spinning Slash|d|Undying Rage|h
drmundo|Dr. Mundo|2009|T|#8a5fb0|Infected Bonesaw|n|Maximum Dosage|h
katarina|Katarina|2009
nidalee|Nidalee|2009|M|#5fa05a|Javelin Toss|n|Aspect of the Cougar|d
udyr|Udyr|2009|F|#a0603a|Wilding Claw|n|Wingborne Storm|s
heimerdinger|Heimerdinger|2009|M|#d9c25a|CH-2 Electron Storm Grenade|x|UPGRADE!!!|a
corki|Corki|2009|D|#d9a03a|Phosphorus Bomb|a|Missile Barrage|n
shaco|Shaco|2009|A|#c04a3a|Deceive|d|Hallucinate|s
nasus|Nasus|2009|F|#b0904a|Siphoning Strike|n|Fury of the Sands|r
poppy|Poppy|2010
garen|Garen|2010
galio|Galio|2010
xinzhao|Xin Zhao|2010
sona|Sona|2010
swain|Swain|2010
lux|Lux|2010
cassio|Cassiopeia|2010
leblanc|LeBlanc|2010
mordekaiser|Mordekaiser|2010
vladimir|Vladimir|2010
gragas|Gragas|2010|F|#b0703a|Barrel Roll|a|Explosive Cask|x
pantheon|Pantheon|2010|F|#c09a3a|Comet Spear|n|Grand Starfall|d
ezreal|Ezreal|2010|D|#e0b04a|Mystic Shot|n|Trueshot Barrage|a
irelia|Irelia|2010|F|#c04f6a|Bladesurge|d|Vanguard's Edge|x
kennen|Kennen|2010|M|#7a5fc8|Thundering Shuriken|n|Slicing Maelstrom|x
akali|Akali|2010|A|#3fa06a|Five Point Strike|a|Perfect Execution|d
malzahar|Malzahar|2010|M|#8a4fc0|Call of the Void|a|Nether Grasp|t
olaf|Olaf|2010|F|#c06a3a|Undertow|n|Ragnarok|r
kogmaw|Kog'Maw|2010|D|#9fb03a|Caustic Spittle|n|Living Artillery|a
urgot|Urgot|2010|F|#6f8a5a|Corrosive Charge|a|Fear Beyond Death|e
missfortune|Miss Fortune|2010|D|#c03a4a|Double Up|n|Bullet Time|a
brand|Brand|2010|M|#e0603a|Pillar of Flame|a|Pyroclasm|a
trundle|Trundle|2010|F|#7fa0c0|Chomp|r|Subjugate|r
shen|Shen|2010|T|#4a5fa0|Twilight Assault|n|Stand United|h
thresh|Thresh|2013
quinn|Quinn|2013
lucian|Lucian|2013
jinx|Jinx|2013
yasuo|Yasuo|2013
aatrox|Aatrox|2013|F|#a02a3a|The Darkin Blade|a|World Ender|r
zac|Zac|2013|T|#5fc05a|Stretching Strikes|n|Let's Bounce!|x
velkoz|Vel'Koz|2014|M|#9a5fc0|Plasma Fission|n|Life Form Disintegration Ray|a
braum|Braum|2014|S|#7fb0d8|Winter's Bite|t|Glacial Fissure|x
gnar|Gnar|2014|F|#d98a3a|Boomerang Throw|n|GNAR!|x
azir|Azir|2014|M|#e0c05a|Conquering Sands|a|Emperor's Divide|x
kalista|Kalista|2014|D|#5fc0b0|Pierce|n|Rend|e
reksai|Rek'Sai|2014|F|#8a5fa0|Queen's Wrath|n|Void Rush|e
bard|Bard|2014|S|#e0c08a|Cosmic Binding|t|Tempered Fate|x
ekko|Ekko|2015|A|#3fd0c0|Timewinder|a|Chronobreak|h
tahmkench|Tahm Kench|2015|T|#5f8a7a|Tongue Lash|t|Devour|e
kindred|Kindred|2015|D|#d8d8e8|Dance of Arrows|d|Lamb's Respite|h
illaoi|Illaoi|2015|F|#3fa08a|Tentacle Smash|a|Leap of Faith|s
jhin|Jhin|2016|D|#c04a5a|Dancing Grenade|n|Curtain Call|e
aurelionsol|Aurelion Sol|2016|M|#4f6fd8|Breath of Light|a|Falling Star|x
taliyah|Taliyah|2016|M|#c0a07a|Threaded Volley|n|Weaver's Wall|x
kled|Kled|2016
ivern|Ivern|2016|S|#7fbf6a|Rootcaller|t|Daisy!|x
camille|Camille|2016|F|#5f7fa0|Hookshot|d|The Hextech Ultimatum|e
xayah|Xayah|2017|D|#a04fb0|Double Daggers|n|Featherstorm|a
rakan|Rakan|2017|S|#d9a03a|Grand Entrance|x|The Quickness|x
kayn|Kayn|2017|A|#4f3fa0|Reaping Slash|s|Umbral Trespass|e
ornn|Ornn|2017|T|#c06a3a|Volcanic Rupture|a|Call of the Forge God|x
zoe|Zoe|2017|M|#e06ab0|Paddle Star!|n|Portal Jump|d
kaisa|Kai'Sa|2018|D|#7a4fc8|Icathian Rain|n|Killer Instinct|d
pyke|Pyke|2018|A|#3f8a8a|Bone Skewer|t|Death from Below|e
neeko|Neeko|2018|M|#5fd08a|Blooming Burst|a|Pop Blossom|x
sylas|Sylas|2019
yuumi|Yuumi|2019|S|#8ab0e8|Prowling Projectile|n|Final Chapter|x
qiyana|Qiyana|2019|A|#3fb08a|Edge of Ixtal|n|Supreme Display of Talent|x
senna|Senna|2019|D|#5f6f7a|Piercing Darkness|h|Dawning Shadow|a
aphelios|Aphelios|2019|D|#6f8ac0|Infernum|a|Moonlight Vigil|a
sett|Sett|2019|F|#c05a3a|Knuckle Down|n|The Show Stopper|x
lillia|Lillia|2020|M|#d88ab0|Blooming Blows|s|Lilting Lullaby|x
yone|Yone|2020|F|#5a6fc0|Mortal Steel|d|Fate Sealed|x
samira|Samira|2020
seraphine|Seraphine|2020|M|#e08ac0|High Note|n|Encore|x
rell|Rell|2020
viego|Viego|2020|A|#3fa08a|Blade of the Ruined King|n|Heartbreaker|e
gwen|Gwen|2021|F|#8ab0d8|Snip Snip!|r|Needlework|n
akshan|Akshan|2021|D|#3f9a6a|Avengerang|n|Comeuppance|e
vex|Vex|2021|M|#5a5a6a|Mistral Bolt|n|Shadow Surge|d
zeri|Zeri|2021|D|#7fd04f|Burst Fire|n|Lightning Crash|a
renata|Renata Glasc|2022|S|#a04f8a|Handshake|t|Hostile Takeover|x
belveth|Bel'Veth|2022|F|#7a3fa0|Void Surge|d|Endless Banquet|r
nilah|Nilah|2022|F|#3fb0c8|Formless Blade|n|Apotheosis|r
ksante|K'Sante|2022|T|#6a5a3a|Ntofo Strikes|n|All Out|d
milio|Milio|2023|S|#e09a4a|Ultra Mega Fire Kick|t|Breath of Life|h
naafiri|Naafiri|2023|A|#a06a5a|Darkin Daggers|n|The Call of the Pack|d
briar|Briar|2023
hwei|Hwei|2023|M|#6a5ac0|Devastating Fire|n|Spiraling Despair|a
smolder|Smolder|2023|D|#e07a3a|Super Scorcher Breath|n|MMOOOMMMM!|a
aurora|Aurora|2024|M|#7ab0e0|Twofold Hex|n|Between Worlds|x
ambessa|Ambessa|2024|F|#a03a3a|Cunning Sweep|s|Public Execution|t
mel|Mel|2025|M|#e0c08a|Radiant Volley|n|Golden Eclipse|a
`;

  const ROLE = { T: "tank", F: "fighter", A: "assassin", M: "mage", D: "marksman", S: "support" };
  const TYPE = { n: "nuke", a: "aoe", s: "spin", d: "dash", t: "stun", x: "aoestun", h: "heal", e: "execute", r: "drain" };
  const ROSTER = root.LOL.ROSTER;

  TABLE.trim().split("\n").forEach((line) => {
    const [id, name, year, role, color, q, qt, r, rt] = line.split("|").map((s) => s.trim());
    if (ROSTER[id]) { ROSTER[id].year = Number(year); return; }
    if (!role) throw new Error("Champion " + id + " absent de src/roster.js : il faut décrire ses sorts.");
    const ult = { name: r, type: TYPE[rt] };
    if (TYPE[rt] === "stun") ult.stun = 2.0; // ex. la flèche d'Ashe
    ROSTER[id] = { name, year: Number(year), role: ROLE[role], color, spell: { name: q, type: TYPE[qt] }, ult };
  });

  // années des autres champions du roster de base (pour d'autres affiches)
  const YEARS = { jarvan: 2011, fiora: 2012, shyvana: 2011, vayne: 2011, darius: 2012, draven: 2012, talon: 2011, riven: 2011, ahri: 2011, zed: 2012, leesin: 2011 };
  Object.keys(YEARS).forEach((id) => { if (ROSTER[id] && !ROSTER[id].year) ROSTER[id].year = YEARS[id]; });
})(typeof window !== "undefined" ? window : globalThis);
