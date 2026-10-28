SPARTA ARENA PC - TEMİZ BAŞLANGIÇ

BU PAKETİN İÇERİĞİ
- main.py: klavye ile oynanan bağımsız PC sürümü
- requirements.txt: Pygame bağımlılığı
- Oyunu_Baslat.bat: Python kurulu bilgisayarda oyunu başlatır
- EXE_Olustur.bat: bilgisayarda EXE oluşturmayı dener
- .github/workflows/windows-build.yml: GitHub Actions ile Windows EXE oluşturur

GITHUB'A YÜKLEME
1. Yeni, boş bir GitHub deposu oluştur: Sparta-Arena-PC.
2. Bu ZIP'i bilgisayarında Tümünü Ayıkla ile çıkar.
3. Depoda Add file > Upload files yoluyla kökteki main.py, requirements.txt,
   Oyunu_Baslat.bat, EXE_Olustur.bat, Windows_Kurulum.txt dosyalarını yükle ve commit et.
4. Sonra Add file > Create new file seç.
5. Dosya adını .github/workflows/windows-build.yml yap.
6. Ayıklanmış paketteki .github/workflows/windows-build.yml dosyasının içeriğini
   GitHub editörüne yapıştır ve commit et.
7. Actions > Sparta Arena Windows Build > Run workflow adımlarını uygula.
8. Başarılı çalışmanın altındaki Artifacts bölümünden Sparta-Arena-Windows dosyasını indir.
9. ZIP'i ayıkla ve SpartaArena.exe dosyasını çalıştır. EXE'nin yanındaki diğer dosyaları
   aynı klasörde tut; sadece EXE dosyasını ayırma.

ÖNEMLİ
- ZIP dosyasının kendisini depoya yüklemek yeterli değildir. İçindeki dosyalar köke yüklenmelidir.
- Bu, bağımsız PC sürümüdür; Android/Pydroid projesinin bütün özelliklerinin birebir kopyası değildir.
