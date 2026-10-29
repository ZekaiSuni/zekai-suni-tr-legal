"""GitHub Pages statik demo derleyicisi:
- docs/demo/ altına 18 sayfanın statik sürümünü üretir (api shim + gömülü veri)
- docs/static/ altına ortak varlıkları kopyalar
- docs/index.html'e "Demo Başlat" düğmesi ekler
Çalıştırma: python araclar/pages_demo.py"""
import os
import re
import shutil

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(KOK, "docs")

SAYFALAR = ["index.html", "playbook.html", "masa.html", "inceleme.html", "dosya.html",
            "kabul.html", "atif.html", "kronoloji.html", "qa.html", "envanter.html",
            "mevzuat.html", "kesif.html", "izleme.html", "harcama.html", "uyum.html",
            "portfoy.html", "patent.html", "matris.html"]

VARLIKLAR = ["styles.css", "nav.js", "ortak.js", "giris.js", "app.js",
             "demo-veri.js", "demo-kopru.js", "mevzuat-zaman.js"]

def main():
    hedef_statik = os.path.join(DOCS, "static")
    hedef_demo = os.path.join(DOCS, "demo")
    os.makedirs(hedef_statik, exist_ok=True)
    os.makedirs(hedef_demo, exist_ok=True)

    # varlıklar
    for f in VARLIKLAR:
        src = os.path.join(KOK, "static", f)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(hedef_statik, f))
    # görseller
    img_src = os.path.join(DOCS, "img")
    if os.path.isdir(img_src):
        shutil.copytree(img_src, os.path.join(hedef_statik, "img"), dirs_exist_ok=True)

    # sayfalar: /static/ → ../static/, shim'i head'e sok, demo bandı bayrağı
    for sayfa in SAYFALAR:
        src = os.path.join(KOK, "static", sayfa)
        icerik = open(src, encoding="utf-8").read()
        icerik = icerik.replace('"/static/', '"../static/')
        icerik = icerik.replace("='/static/", "='../static/")
        # shim en başa (head içine): veri + köprü, sırasıyla
        shim = ('<script>window.ZEKAI_STATIK=true;window.ZK_NAV_PRO="..";</script>\n'
                '<script src="../static/demo-veri.js"></script>\n'
                '<script src="../static/demo-kopru.js"></script>\n')
        icerik = icerik.replace("</head>", shim + "</head>", 1)
        # sayfalar app.js'i kendileri yüklemiyorsa (atif, mevzuat vb.) bile shim çalışır
        with open(os.path.join(hedef_demo, sayfa), "w", encoding="utf-8") as f:
            f.write(icerik)
    print("18 demo sayfası üretildi → docs/demo/")

    # landing'e demo düğmesi
    yol_landing = os.path.join(DOCS, "index.html")
    icerik = open(yol_landing, encoding="utf-8").read()
    if "demo/index.html" not in icerik:
        eski = '<div class="pill">Türk Hukuku · 18 modül · insan onaylı yapay zeka</div>'
        yeni = ('<div class="pill">Türk Hukuku · 18 modül · insan onaylı yapay zeka</div>\n'
                '    <div style="margin-top:20px"><a href="demo/index.html" '
                'style="display:inline-block;background:#141413;color:#fff;text-decoration:none;'
                'border-radius:10px;padding:12px 26px;font-size:16px;font-weight:600">'
                '▶ Çalışan Demoyu Başlat</a></div>')
        icerik = icerik.replace(eski, yeni, 1)
        open(yol_landing, "w", encoding="utf-8").write(icerik)
        print("landing'e demo düğmesi eklendi")

if __name__ == "__main__":
    main()
