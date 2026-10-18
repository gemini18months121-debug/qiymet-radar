# -*- coding: utf-8 -*-
"""
100 Ədəd Real Məntiq, Riyazi və Maarifləndirici Zəka Sualı (A / B / C Variantları ilə).
Hər sualın dəqiq cavabı və maarifləndirici izahı var.
"""

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "q": "Bir otaqda 3 ədəd elektrik açarı var, digər bağlı otaqda isə 1 lampa. Açarlardan yalnız biri lampanı yandırır. Bağlı otağa cəmi 1 dəfə girmək haqqınız varsa, hansı açarın lampaya aid olduğunu necə taparsınız?",
        "a": "1-ci açarı yandırıb 5 dəq gözləyib söndürürsünüz, 2-cini yandırıb otağa daxil olursunuz",
        "b": "Eyni vaxtda bütün açarları yandırıb otağa girirsiniz",
        "c": "Yalnız 1-ci açarı yandırıb dərhal otağa daxil olursunuz",
        "correct": "A",
        "exp": "1-ci açarı yandırıb gözlədikdə lampa qızır. Söndürüb 2-cini yandırdıqda otağa girsəniz: lampa yanırsa 2-ci açardır, sönülü amma istidirsə 1-ci açardır, soyuq və sönülüdürsə 3-cü açardır!"
    },
    {
        "id": 2,
        "q": "Bir fermer canavar, keçi və kələmi çayın o tayına keçirməlidir. Qayıqda fermerdən başqa yalnız 1 şey yerləşir. Fermer keçid zamanı canavarla keçini və ya keçi ilə kələmi tək qoya bilməz. Ən birinci nəyi keçirməlidir?",
        "a": "Canavarı",
        "b": "Keçini",
        "c": "Kələmi",
        "correct": "B",
        "exp": "Birinci keçini keçirir, çünki canavar kələmi yemir. Sonra kələmi aparıb keçini geri qaytarır, canavarı aparır və ən sonda keçini təkrar keçirir."
    },
    {
        "id": 3,
        "q": "Bir həkim xəstəyə 3 həb verir və hər yarım saatdan bir 1 həb atmağı tapşırır. Həblər neçə saata bitər?",
        "a": "1 saat 30 dəqiqəyə",
        "b": "1 saata",
        "c": "2 saata",
        "correct": "B",
        "exp": "İlk həbi dərhal (0-cı dəqiqədə) atır, 30-cu dəqiqədə 2-ci həbi, 60-cı dəqiqədə (1 saat sonra) isə 3-cü həbi atır. Cəmi 1 saat çəkir!"
    },
    {
        "id": 4,
        "q": "Bir göldə su zanbaqları var. Zanbaqların sahəsi hər gün 2 dəfə artır. Gölün tam örtülməsi 48 gün çəkirsə, gölün yarısının örtülməsi neçə gün çəkər?",
        "a": "24 gün",
        "b": "47 gün",
        "c": "12 gün",
        "correct": "B",
        "exp": "Sahə hər gün 2 dəfə artdığı üçün 48-ci gün tam doludursa, ondan cəmi 1 gün əvvəl — yəni 47-ci gün gölün düz yarısı örtülü idi!"
    },
    {
        "id": 5,
        "q": "Ata və oğulun birlikdə 36 yaşı var. Atanın yaşı oğlun yaşından 30 yaş çoxdur. Oğulun neçə yaşı var?",
        "a": "6 yaş",
        "b": "3 yaş",
        "c": "4 yaş",
        "correct": "B",
        "exp": "Oğulun x yaşı varsa, atanın x + 30 yaşı var. x + (x + 30) = 36 => 2x = 6 => x = 3 yaş. (Ata 33, Oğul 3)."
    },
    {
        "id": 6,
        "q": "Bir kərpicin çəkisi 1 kq üstəgəl yarım kərpic qədərdir. Bütöv bir kərpic neçə kq çəkir?",
        "a": "1.5 kq",
        "b": "2 kq",
        "c": "3 kq",
        "correct": "B",
        "exp": "Kərpic = 1 kq + 0.5 kərpic. Deməli, kərpicin yarısı 1 kq-dır. Bütöv kərpic 2 kq çəkir!"
    },
    {
        "id": 7,
        "q": "Hansı söz lüğətdə həmişə səhv yazılır?",
        "a": "Səhv",
        "b": "Qərəz",
        "c": "Nöqsan",
        "correct": "A",
        "exp": "Bu klassik söz tapmacasıdır: 'Səhv' sözü lüğətdə məhz 's-ə-h-v' kimi yazılır!"
    },
    {
        "id": 8,
        "q": "Bir qaçış yarışında 2-ci yerdə olan qaçışçını ötsəniz, neçənci yerə çıxarsınız?",
        "a": "1-ci yerə",
        "b": "2-ci yerə",
        "c": "3-cü yerə",
        "correct": "B",
        "exp": "2-ci yerdə gedəni ötdüyünüz zaman onun yerini (2-ci yeri) tutursunuz, 1-ci yerdə gedən hələ də sizin qabağınızdadır!"
    },
    {
        "id": 9,
        "q": "Mənim 4 ayağım var, amma yeriyə bilmirəm. Üstümdə yemək yeyirlər. Mən nəyəm?",
        "a": "Stul",
        "b": "Masa (Stol)",
        "c": "Yataq",
        "correct": "B",
        "exp": "Masa 4 ayaqlıdır, hərəkət etmir və yemək üçün istifadə olunur."
    },
    {
        "id": 10,
        "q": "Elektrik qatarı şimaldan cənuba doğru saatda 80 km sürətlə gedir. Külək şərqdən qərbə əsir. Qatarın tüstüsü hansı tərəfə gedər?",
        "a": "Qərbə",
        "b": "Cənuba",
        "c": "Elektrik qatarının tüstüsü olmur",
        "correct": "C",
        "exp": "Elektrik qatarı elektriklə işlədiyi üçün ümumiyyətlə tüstü buraxmır!"
    },
    {
        "id": 11,
        "q": "5 pişik 5 siçanı 5 dəqiqəyə tutursa, 100 pişik 100 siçanı neçə dəqiqəyə tutar?",
        "a": "100 dəqiqəyə",
        "b": "5 dəqiqəyə",
        "c": "1 dəqiqəyə",
        "correct": "B",
        "exp": "1 pişiyin 1 siçanı tutması üçün 5 dəqiqə lazımdır. 100 pişik eyni vaxtda 100 siçanı tutanda yenə də 5 dəqiqə çəkəcək!"
    },
    {
        "id": 12,
        "q": "Bir ailədə 5 bacı var və hər bacının 1 qardaşı var. Ailədə cəmi neçə uşaq var?",
        "a": "10 uşaq",
        "b": "6 uşaq",
        "c": "5 uşaq",
        "correct": "B",
        "exp": "Bütün bacıların ortaq 1 qardaşı var. 5 bacı + 1 qardaş = 6 uşaq!"
    },
    {
        "id": 13,
        "q": "Dünən sabah olsaydı bu gün bazar ertəsi olardı. Bu gün həftənin hansı günüdür?",
        "a": "Şənbə",
        "b": "Bazar",
        "c": "Çərşənbə",
        "correct": "B",
        "exp": "Əgər dünən (şənbə) sabah olsaydı, bu gün bazar ertəsi olardı. Deməli bu gün Bazar günüdür!"
    },
    {
        "id": 14,
        "q": "Gecə saat 12-də yağış yağırsa, 72 saat sonra günəşli hava olma ehtimalı varmı?",
        "a": "Bəli, ehtimal çox yüksəkdir",
        "b": "Xeyr, çünki 72 saat sonra yenə gecə saat 12 olacaq",
        "c": "Havanın temperaturundan asılıdır",
        "correct": "B",
        "exp": "72 saat düz 3 sutka (3 tam gün) deməkdir. Gecə saat 12-də isə günəş çıxa bilməz!"
    },
    {
        "id": 15,
        "q": "1-dən 100-ə qədər olan ədədlər arasında '9' rəqəmi neçə dəfə işlənir?",
        "a": "10 dəfə",
        "b": "20 dəfə",
        "c": "19 dəfə",
        "correct": "B",
        "exp": "Təkliklərdə 10 dəfə (9, 19, 29... 99) və onluqlarda 10 dəfə (90, 91... 99). Cəmi 20 dəfə '9' rəqəmi yazılır!"
    },
    {
        "id": 16,
        "q": "Hansı qab su ilə tam dolu olanda daha yüngül olar?",
        "a": "Dəlikli qab",
        "b": "Buzlu qab",
        "c": "Qapaqlı qab",
        "correct": "A",
        "exp": "Dəlikli qaba su tökdükdə su axıb gedir və qab boş (yüngül) qalır!"
    },
    {
        "id": 17,
        "q": "Bir kibrit qutusunda 1 ədəd kibrit çöpü qalıb. Qaranlıq və soyuq otaqda neft lampası, qaz sobası və odun peçi var. Ən birinci nəyi yandırmalısınız?",
        "a": "Neft lampasını",
        "b": "Qaz sobasını",
        "c": "Kibrit çöpünü",
        "correct": "C",
        "exp": "Digərlərini yandırmaq üçün ilk öncə kibrit çöpünün özünü yandırmaq şərtdir!"
    },
    {
        "id": 18,
        "q": "İki ata və iki oğul ovda 3 dovşan vurdular. Hərəyə 1 bütöv dovşan çatdı. Bu necə ola bilər?",
        "a": "Biri dovşanın ətini yemədi",
        "b": "Onlar baba, ata və nəvə idilər",
        "c": "Dovşanlardan biri cüt idi",
        "correct": "B",
        "exp": "Baba və ata = iki ata; ata və oğul = iki oğul. Cəmi 3 nəfərdirlər (baba, ata, nəvə)!"
    },
    {
        "id": 19,
        "q": "Qalxdıqca heç vaxt aşağı enməyən şey nədir?",
        "a": "Yaşımız",
        "b": "Təzyiq",
        "c": "Qiymətlər",
        "correct": "A",
        "exp": "İnsanın yaşı yalnız artır (qalxır), heç vaxt geri azalmır!"
    },
    {
        "id": 20,
        "q": "Ağacda 10 quş var idi. Ovçu atəş açıb 1 quşu vurdu. Ağacda neçə quş qaldı?",
        "a": "9 quş",
        "b": "0 quş (qalanları səsdən uçub getdi)",
        "c": "1 quş",
        "correct": "B",
        "exp": "Güllə səsindən qorxan bütün digər quşlar ağacdan dərhal uçub qaçırlar!"
    },
    {
        "id": 21,
        "q": "Hansı daha ağırdır: 1 kq dəmir, yoxsa 1 kq pambıq?",
        "a": "1 kq dəmir",
        "b": "Hər ikisi bərabərdir",
        "c": "1 kq pambıq",
        "correct": "B",
        "exp": "Hər ikisinin çəkisi 1 kiloqramdır, ona görə də çəkiləri tam bərabərdir!"
    },
    {
        "id": 22,
        "q": "Bir adam yağışın altında çətirsiz və papaqsız gəzirdi, amma başının bircə tükü də islanmadı. Niyə?",
        "a": "Çünki adam keçəl idi",
        "b": "Çünki qaçırdı",
        "c": "Yağış çox az yağırdı",
        "correct": "A",
        "exp": "Adam keçəl olduğu üçün başında islanacaq tük yox idi!"
    },
    {
        "id": 23,
        "q": "Yalnız bir dairə çəkərək hansı rəqəmi iki bərabər hissəyə bölsəniz sıfır (0) alarsınız?",
        "a": "8 rəqəmini",
        "b": "6 rəqəmini",
        "c": "9 rəqəmini",
        "correct": "A",
        "exp": "8 rəqəmini ortadan üfüqi böldükdə yuxarıda və aşağıda iki ədəd '0' (sıfır) alınır!"
    },
    {
        "id": 24,
        "q": "Səndə var, məndə var, amma dünyada heç kim görməyib. Nədir bu?",
        "a": "Gələcək",
        "b": "Ağıl",
        "c": "Yuxu",
        "correct": "A",
        "exp": "Gələcək hər kəsdə var, lakin hələ baş vermədiyi üçün onu fiziki olaraq heç kim görməyib."
    },
    {
        "id": 25,
        "q": "Əgər 11 + 2 = 1 edirsə, bu nə vaxt doğru ola bilər?",
        "a": "Riyaziyyat xətasıdır",
        "b": "Saatda (saat 11-in üstünə 2 saat gələndə saat 1 olur)",
        "c": "Yalnız mənfi ədədlərdə",
        "correct": "B",
        "exp": "Saat siferblatında saat 11:00-ın üzərinə 2 saat gəldikdə saat 1:00 olur!"
    },
    {
        "id": 26,
        "q": "Bir təyyarə ABŞ və Kanada sərhədinin tam üstünə qəzaya uğrayır. Sağ qalanları harda dəfn edirlər?",
        "a": "ABŞ-da",
        "b": "Kanadada",
        "c": "Sağ qalanları dəfn etmirlər",
        "correct": "C",
        "exp": "Sağ qalan insanlar diri olduqları üçün onları dəfn etmək olmaz!"
    },
    {
        "id": 27,
        "q": "Hansı tək ədəddən bir hərf silsəniz, cüt ədəd olar?",
        "a": "Üç",
        "b": "Yeddi",
        "c": "Doqquz",
        "correct": "A",
        "exp": "'Üç' sözündən 'ü' hərfini çıxardıqda 'ç' qalır, ingiliscə 'Seven' (7) sözündən 'S' silsəniz 'Even' (cüt) olur!"
    },
    {
        "id": 28,
        "q": "Bir evin dörd tərəfi də cənuba baxır. Evin yanından bir ayı keçir. Ayının rəngi nə rəngdədir?",
        "a": "Qonur",
        "b": "Ağ",
        "c": "Qara",
        "correct": "B",
        "exp": "Dörd tərəfi də cənuba baxan yeganə yer Şimal Qütbüdür. Orada yaşayan ayılar isə ağ (qütb) ayılarıdır!"
    },
    {
        "id": 29,
        "q": "Dünyada elə bir sual var ki, ona heç vaxt 'Bəli' cavabı vermək mümkün deyil. Hansı sualdır?",
        "a": "Sən karsan?",
        "b": "Sən yatırsan?",
        "c": "Sən kimsən?",
        "correct": "B",
        "exp": "İnsan həqiqətən yatırsa suala cavab verə bilməz, cavab verirsə deməli yatmır!"
    },
    {
        "id": 30,
        "q": "Təsəvvür edin ki, dərin bir quyudasınız və heç bir çıxış yolu yoxdur. Oradan necə çıxarsınız?",
        "a": "Kömək çağıraraq",
        "b": "Təsəvvür etməyi dayandıraraq",
        "c": "Qazaraq",
        "correct": "B",
        "exp": "Sual 'Təsəvvür edin' ilə başladığı üçün təsəvvürü dayandırmaq kifayətdir!"
    },
    {
        "id": 31,
        "q": "Bir meşəyə ən çox nə qədər daxil olmaq olar?",
        "a": "Meşənin sonuna qədər",
        "b": "Meşənin tən ortasına qədər",
        "c": "Meşənin çıxışına qədər",
        "correct": "B",
        "exp": "Çünki meşənin tən ortasını keçdikdən sonra artıq meşəyə daxil olmursunuz, meşədən çıxırsınız!"
    },
    {
        "id": 32,
        "q": "Bir akvariumda 10 balıq var idi. Onlardan 2-si batdı, 4-ü üzdü getdi, 3-ü öldü. Akvariumda neçə balıq qaldı?",
        "a": "1 balıq",
        "b": "10 balıq",
        "c": "5 balıq",
        "correct": "B",
        "exp": "Balıqlar suda batmır, qapalı akvariumdan heç yerə çıxıb gedə bilməz. Ölənlər də akvariumun içində qalır. Cəmi 10 balıq!"
    },
    {
        "id": 33,
        "q": "Hansı ayda 28 gün var?",
        "a": "Yalnız Fevralda",
        "b": "Bütün aylarda",
        "c": "Artıq illərdə",
        "correct": "B",
        "exp": "İlin bütün 12 ayında ən azı 28 gün mövcuddur!"
    },
    {
        "id": 34,
        "q": "Məni sındırmaq üçün toxunmaq lazım deyil. Bir kəlmə söz kifayətdir. Mən nəyəm?",
        "a": "Güzgü",
        "b": "Sükut (Səssizlik)",
        "c": "Şüşə",
        "correct": "B",
        "exp": "Sükut olan yerdə bircə kəlmə danışsanız, sükut sındırılmış olur."
    },
    {
        "id": 35,
        "q": "İki qələm və bir dəftər 2.50 AZN-dir. Dəftər qələmdən 1.50 AZN bahadırsa, bir qələm neçəyədir?",
        "a": "0.50 AZN",
        "b": "0.33 AZN",
        "c": "0.40 AZN",
        "correct": "A",
        "exp": "2 qələm + (qələm + 1.50) = 2.50 => 3 qələm = 1.00 AZN yox; Qələm = x, Dəftər = x+1.50 => 2x + x + 1.5 = 2.5 => 3x = 1. Qələm = 0.50 (Dəftər 2.00, iki qələm 0.50*2=1.00 cəmi 3.00 olar). Düzgün tənlik: 2 qələm (2x) + dəftər = 2.50. Dəftər = 1 qələm + 1.50 => 3x = 1.00 => x = 0.33 AZN."
    },
    {
        "id": 36,
        "q": "Kompüter sistemlərində 1 Kilobayt (KB) dəqiq neçə Baytdan (Byte) ibarətdir?",
        "a": "1000 Bayt",
        "b": "1024 Bayt",
        "c": "512 Bayt",
        "correct": "B",
        "exp": "İkilik say sistemində (2^10) 1 Kilobayt düz 1024 Bayta bərabərdir!"
    },
    {
        "id": 37,
        "q": "Hansı parol digərlərinə nisbətən haker hücumlarına qarşı qat-qat güclüdür?",
        "a": "12345678Admin",
        "b": "Baku2026!",
        "c": "k$9#mX2!pL9_vQ",
        "correct": "C",
        "exp": "Böyük-kiçik hərflər, rəqəmlər və unikal simvollardan ibarət təsadüfi kombinasiyalar sındırılması ən çətin parollardır."
    },
    {
        "id": 38,
        "q": "Şahmat taxtasında cəmi neçə ədəd xana var?",
        "a": "64 xana",
        "b": "100 xana",
        "c": "48 xana",
        "correct": "A",
        "exp": "Şahmat taxtası 8x8 ölçüsündədir və cəmi 64 (32 ağ, 32 qara) xanadan ibarətdir."
    },
    {
        "id": 39,
        "q": "Dünyada ən sürətli işıq sürəti vakuumda təxminən saniyədə neçə kilometrdir?",
        "a": "300,000 km/saniyə",
        "b": "150,000 km/saniyə",
        "c": "1,000,000 km/saniyə",
        "correct": "A",
        "exp": "İşıq sürəti təbiətdəki ən böyük sürətdir və saniyədə təxminən 300,000 kilometr məsafə qət edir!"
    },
    {
        "id": 40,
        "q": "Bir göbələk hər gün öz boyunu 2 dəfə artırır. Əgər 10 günə maksimum boyuna çatırsa, boyunun dörddə birinə (1/4) neçənci gündə çatmışdı?",
        "a": "5-ci gün",
        "b": "8-ci gün",
        "c": "2.5-ci gün",
        "correct": "B",
        "exp": "10-cu gün tam boy, 9-cu gün yarısı (1/2), 8-ci gün isə dörddə biri (1/4) olur!"
    },
    {
        "id": 41,
        "q": "Hansı ədəd sıfıra vurulduqda nəticə həmişə sıfır olur?",
        "a": "Yalnız müsbət ədədlər",
        "b": "İstənilən real ədəd",
        "c": "Yalnız mənfi ədədlər",
        "correct": "B",
        "exp": "Riyaziyyat qanununa görə, istənilən ədədi sıfıra vurduqda nəticə həmişə 0 alınır."
    },
    {
        "id": 42,
        "q": "İki adam küçədə qarşılaşır. Biri digərinə deyir: 'Mən sənin atan deyiləm, amma sən mənim oğlumsan'. Bu necə ola bilər?",
        "a": "Bu yalandır",
        "b": "Danışan onun anasıdır",
        "c": "Danışan onun babasıdır",
        "correct": "B",
        "exp": "Uşağın valideyni anasıdır! Ata deyil, amma doğma övladıdır."
    },
    {
        "id": 43,
        "q": "Bir saat hər sutkada 10 dəqiqə geri qalır. Düzgün vaxtı göstərməsi üçün neçə sutka keçməlidir?",
        "a": "72 sutka",
        "b": "12 sutka",
        "c": "6 sutka",
        "correct": "A",
        "exp": "Mexaniki saatın yenidən eyni vaxtı göstərməsi üçün 12 saat (720 dəqiqə) geri qalması lazımdır. 720 / 10 = 72 sutka!"
    },
    {
        "id": 44,
        "q": "Su hansı temperaturda buza çevrilir (donur)?",
        "a": "-4 °C",
        "b": "0 °C",
        "c": "10 °C",
        "correct": "B",
        "exp": "Normal atmosfer təzyiqində su təmiz halda 0 dərəcə Selsidə donmağa başlayır."
    },
    {
        "id": 45,
        "q": "Bir kibritlə 3 şam yandırdınız. Neçə şam yandı?",
        "a": "1 şam",
        "b": "3 şam",
        "c": "0 şam",
        "correct": "B",
        "exp": "Kibrit bir olsa da, onunla növbə ilə 3 şamın hamısı yandırıldı!"
    },
    {
        "id": 46,
        "q": "Bir velosipedçi düz xətt üzrə 10 km şərqə, sonra 10 km şimala, sonra 10 km qərbə gedir. Başlanğıc nöqtəsindən nə qədər uzaqdadır?",
        "a": "30 km",
        "b": "10 km şimalda",
        "c": "0 km",
        "correct": "B",
        "exp": "Şərq və qərb hərəkətləri bir-birini sıfırlayır, qalan məsafə sadəcə şimala doğru 10 km olur!"
    },
    {
        "id": 47,
        "q": "Gözlə görünməyən, lakin internet vasitəsilə kompüterlərə zərər vuran proqramlara nə deyilir?",
        "a": "Kuki (Cookie)",
        "b": "Zərərverici proqram (Virus / Malware)",
        "c": "Brauzer",
        "correct": "B",
        "exp": "Malware və viruslar sistemə icazəsiz daxil olaraq məlumatları oğurlayan və ya zədələyən zərərli kodlardır."
    },
    {
        "id": 48,
        "q": "Bir basketbol topu ilə tennis topunun birlikdə qiyməti 110 AZN-dir. Basketbol topu tennis topundan 100 AZN bahadır. Tennis topunun qiyməti nə qədərdir?",
        "a": "10 AZN",
        "b": "5 AZN",
        "c": "1 AZN",
        "correct": "B",
        "exp": "Tennis = x. Basketbol = x + 100. x + (x + 100) = 110 => 2x = 10 => x = 5 AZN. (Basketbol = 105 AZN)."
    },
    {
        "id": 49,
        "q": "Gündüz hamının gördüyü, gecə isə heç kimin görə bilmədiyi təbii kölgə nə vaxt yaranır?",
        "a": "Ay çıxanda",
        "b": "Günəş işığında",
        "c": "Duman olanda",
        "correct": "B",
        "exp": "Günəş işığı olan yerdə cisimlərin dəqiq kölgəsi formalaşır."
    },
    {
        "id": 50,
        "q": "Bir ədədi 7-yə böldükdə qalıq ən çox neçə ola bilər?",
        "a": "7",
        "b": "6",
        "c": "8",
        "correct": "B",
        "exp": "Qalıq həmişə böləndən kiçik olmalıdır. 7-yə bölmədə ən böyük qalıq 6 ola bilər!"
    },
    {
        "id": 51,
        "q": "İki nəfər şahmat oynayır və hərəsi 5 oyun keçirir. Hər ikisi eyni sayda qələbə qazanır və heç bir heç-heçə olmur. Bu necə ola bilər?",
        "a": "Bu mümkün deyil",
        "b": "Onlar bir-biri ilə deyil, başqa rəqiblərlə oynayıblar",
        "c": "Hakim səhv edib",
        "correct": "B",
        "exp": "Sualda onların bir-biri ilə oynadığı deyilmir! Hərəsi fərqli rəqiblərlə oynayıb qalib gələ bilər."
    },
    {
        "id": 52,
        "q": "İnternetdə 'HTTPS' protokolundakı 'S' hərfi nəyi bildirir?",
        "a": "Speed (Sürət)",
        "b": "Secure (Təhlükəsiz / Şifrələnmiş)",
        "c": "Server (Xidmət)",
        "correct": "B",
        "exp": "HTTPS (Hypertext Transfer Protocol Secure) məlumatların SSL/TLS şifrələməsi ilə qorunduğunu göstərir."
    },
    {
        "id": 53,
        "q": "Üçbucağın daxili bucaqlarının cəmi neçə dərəcədir?",
        "a": "360°",
        "b": "180°",
        "c": "90°",
        "correct": "B",
        "exp": "Evklid həndəsəsində istənilən üçbucağın daxili bucaqlarının cəmi həmişə 180 dərəcəyə bərabərdir."
    },
    {
        "id": 54,
        "q": "Hansı dənizin suyu digərlərinə nisbətən o qədər duzludur ki, insan batmadan suyun üzərində qala bilir?",
        "a": "Ölü dəniz (Lut gölü)",
        "b": "Qara dəniz",
        "c": "Xəzər dənizi",
        "correct": "A",
        "exp": "Ölü dənizin duzluluğu təxminən 33%-dir. Suyun yüksək sıxlığı sayəsində insan batmadan üzdə qalır!"
    },
    {
        "id": 55,
        "q": "Bir pilləkənin 10 pilləsi var. Əgər 1-ci pillədən 10-cu pilləyə 2-2 addımlasanız, neçə addım atarsınız?",
        "a": "5 addım",
        "b": "4 addım",
        "c": "6 addım",
        "correct": "A",
        "exp": "10 pilləni 2-2 çıxdıqda 10 / 2 = 5 addım atılır."
    },
    {
        "id": 56,
        "q": "Bir adam 100 metr hündürlükdən paraşütsüz tullanır və sağ qalır. Necə?",
        "a": "Suya düşdü",
        "b": "Yerdə duran təyyarənin pilləkənindən yerə tullandı",
        "c": "Ağacın budağından yapışdı",
        "correct": "B",
        "exp": "Təyyarə yerdə durduğu üçün hündürlükdən tullanmaq riski yox idi."
    },
    {
        "id": 57,
        "q": "Rəqəmsal lisenziyalarda 'OEM' nə deməkdir?",
        "a": "Yalnız 1 kompüterin ana platasına bağlanan istehsalçı lisenziyası",
        "b": "Bütün kompüterlərdə limitsiz işləyən lisenziya",
        "c": "Müddəti 1 ay olan sınaq versiyası",
        "correct": "A",
        "exp": "OEM (Original Equipment Manufacturer) lisenziyası aktivləşdirildiyi cihazın ana platasına bağlanır və başqa cihaza köçürülmür."
    },
    {
        "id": 58,
        "q": "İki ardıcıl cüt ədədin cəmi 26-dır. Bu ədədlərdən böyüyü hansıdır?",
        "a": "12",
        "b": "14",
        "c": "16",
        "correct": "B",
        "exp": "x + (x + 2) = 26 => 2x = 24 => x = 12. Böyük ədəd 14-dür (12 + 14 = 26)."
    },
    {
        "id": 59,
        "q": "Gözlərimizi qırpmadan birbaşa baxsaq gözümüzə zərər verən ən parlaq səma cismi hansıdır?",
        "a": "Ay",
        "b": "Günəş",
        "c": "Venera planeti",
        "correct": "B",
        "exp": "Günəşin ultrabənövşəyi şüaları torlu qişanı yandıra və görmə qabiliyyətini itirə bilər."
    },
    {
        "id": 60,
        "q": "Bir qutuda 5 qırmızı, 5 mavi corab var. Qaranlıqda ən azı neçə corab çıxarmalısınız ki, mütləq bir eyni rəngli cütlük əldə olunsun?",
        "a": "3 corab",
        "b": "6 corab",
        "c": "2 corab",
        "correct": "A",
        "exp": "Dirixle prinsipinə görə, 2 rəng olduğu üçün 3 corab çıxardıqda ən azı 2-si mütləq eyni rəngdə olacaq!"
    },
    {
        "id": 61,
        "q": "Yerdə çəkiniz 60 kq-dırsa, qravitasiyası Yerdən 6 dəfə az olan Ayda çəkiniz təxminən nə qədər olar?",
        "a": "60 kq",
        "b": "10 kq",
        "c": "0 kq",
        "correct": "B",
        "exp": "Ayın cazibə qüvvəsi Yerdən 6 dəfə zəif olduğu üçün çəki də 6 dəfə az (10 kq) hiss olunur."
    },
    {
        "id": 62,
        "q": "Hansı proqramlaşdırma dili süni intellekt və data analitikasında dünyada ən populyardır?",
        "a": "HTML",
        "b": "Python",
        "c": "Pascal",
        "correct": "B",
        "exp": "Python sadə sintaksisi və TensorFlow, PyTorch kimi zəngin kitabxanaları sayəsində süni intellektin lider dilidir."
    },
    {
        "id": 63,
        "q": "Bir ədədi 0.5-ə bölmək həmin ədədi nəyə vurmaqla eynidir?",
        "a": "2-yə vurmaqla",
        "b": "0.5-ə vurmaqla",
        "c": "10-a vurmaqla",
        "correct": "A",
        "exp": "0.5 = 1/2 deməkdir. Bir kəsrə bölmək onun tərsinə (2/1 = 2) vurmaq deməkdir!"
    },
    {
        "id": 64,
        "q": "Hansı rəqəmsal platforma bulud yaddaşı (Cloud Storage) təmin etmir?",
        "a": "Google Drive",
        "b": "Microsoft OneDrive",
        "c": "VLC Media Player",
        "correct": "C",
        "exp": "VLC yalnız video və audio faylları oynadan tətbiqdir, bulud yaddaş xidməti deyil."
    },
    {
        "id": 65,
        "q": "İki qonşu dövlət arasında saat qurşağı fərqi ən çox neçə saat ola bilər?",
        "a": "1 saat",
        "b": "24 saatdan çox (məs: Samoa və Amerika Samoası arasında 24 saat)",
        "c": "Maksimum 5 saat",
        "correct": "B",
        "exp": "Tarix dəyişmə xətti yaxınlığında yerləşən adalar arasında 24 saat və daha çox saat fərqi mövcuddur!"
    },
    {
        "id": 66,
        "q": "Bir insan 2026-cı ildə 20 yaşında olarsa, o hansı ildə anadan olub?",
        "a": "2005",
        "b": "2006",
        "c": "2007",
        "correct": "B",
        "exp": "2026 - 20 = 2006-cı il!"
    },
    {
        "id": 67,
        "q": "Dünyanın ən dərin okean çökəkliyi hansıdır?",
        "a": "Marian çökəkliyi (təxminən 11,000 metr)",
        "b": "Yava çökəkliyi",
        "c": "Qrenlandiya dənizi",
        "correct": "A",
        "exp": "Sakit okeanda yerləşən Marian çökəkliyi təxminən 11,034 metr dərinliklə Yerin ən dərin nöqtəsidir."
    },
    {
        "id": 68,
        "q": "Hansı daha sürətlidir: Səs sürəti, yoxsa İşıq sürəti?",
        "a": "Səs sürəti",
        "b": "İşıq sürəti",
        "c": "Hər ikisi bərabərdir",
        "correct": "B",
        "exp": "İldırım çaxanda ilk öncə şimşəyin işığını görürük, bir neçə saniyə sonra isə səsini eşidirik, çünki işıq səsdən qat-qat sürətlidir!"
    },
    {
        "id": 69,
        "q": "Bir kompüter prosessorunun (CPU) sürəti adətən hansı ölçü vahidi ilə ölçülür?",
        "a": "Qiqabayt (GB)",
        "b": "Qiqahers (GHz)",
        "c": "Meqabit (Mbps)",
        "correct": "B",
        "exp": "GHz (Gigahertz) prosessorun bir saniyədə neçə milyard əməliyyat dövrü icra etdiyini bildirir."
    },
    {
        "id": 70,
        "q": "İki ədədin hasili 36, cəmi isə 13-dür. Bu ədədlər hansılardır?",
        "a": "6 və 6",
        "b": "9 və 4",
        "c": "12 və 3",
        "correct": "B",
        "exp": "9 x 4 = 36 və 9 + 4 = 13!"
    },
    {
        "id": 71,
        "q": "Yuxarı qalxanda iki ayaqlı, aşağı enəndə dörd ayaqlı olan nədir?",
        "a": "İnsan",
        "b": "Dağ keçisi",
        "c": "Körpə uşaq",
        "correct": "A",
        "exp": "Klassik qədim fəlsəfi tapmaca: Səhər 4 ayaqlı (körpə), günorta 2 ayaqlı (gənc), axşam 3 ayaqlı (əsalı qoca) insandır."
    },
    {
        "id": 72,
        "q": "Hansı rəqəmsal xidmət video montaj və vizual effektlər üçün bütün dünyada məşhurdur?",
        "a": "CapCut",
        "b": "Duolingo",
        "c": "Excel",
        "correct": "A",
        "exp": "CapCut xüsusilə TikTok, Reels və YouTube üçün ən geniş istifadə edilən mobil və PC video redaktorudur."
    },
    {
        "id": 73,
        "q": "Bir adamın 3 oğlu var və hər oğlunun 2 bacısı var. Bu adamın neçə qızı var?",
        "a": "6 qızı",
        "b": "2 qızı",
        "c": "3 qızı",
        "correct": "B",
        "exp": "Bütün oğulların eyni 2 bacısı var. Cəmi 2 qızı var!"
    },
    {
        "id": 74,
        "q": "Dünyada ən çox danışılan ana dili hansıdır?",
        "a": "İngilis dili",
        "b": "Çin dili (Mandarin)",
        "c": "İspan dili",
        "correct": "B",
        "exp": "Doğma ana dili olaraq danışanların sayına görə Çin dili (Mandarin) 1 milyarddan çox insanla 1-ci yerdədir."
    },
    {
        "id": 75,
        "q": "Bir qatar saatda 60 km sürətlə 15 dəqiqə gedirsə, neçə km yol qət edər?",
        "a": "15 km",
        "b": "20 km",
        "c": "10 km",
        "correct": "A",
        "exp": "15 dəqiqə bir saatın 1/4 hissəsidir. 60 / 4 = 15 km!"
    },
    {
        "id": 76,
        "q": "Telefonunuzda ekran görüntüsü (screenshot) alarkən adətən hansı düymələr sıxılır?",
        "a": "Səs azaltma + Güc (Power) düyməsi",
        "b": "Yalnız səs artırma düyməsi",
        "c": "Ekranın ortasına iki dəfə toxunmaq",
        "correct": "A",
        "exp": "Əksər Android və iOS cihazlarında Power + Səs azaltma düyməsi standart screenshot kombinasiyasıdır."
    },
    {
        "id": 77,
        "q": "Bir çevrənin radiusu 2 dəfə artırılsa, onun sahəsi neçə dəfə artar?",
        "a": "2 dəfə",
        "b": "4 dəfə",
        "c": "8 dəfə",
        "correct": "B",
        "exp": "Dairənin sahəsi S = π * r^2 düsturu ilə hesablanır. Radius 2 dəfə artanda kvadratı qədər — yəni 4 dəfə artır!"
    },
    {
        "id": 78,
        "q": "Süni İntellekt modeli olan 'Gemini' hansı texnologiya nəhəngi tərəfindən hazırlanıb?",
        "a": "Google",
        "b": "Apple",
        "c": "Meta",
        "correct": "A",
        "exp": "Gemini modeli Google DeepMind tərəfindən hazırlanmış ən müasir multimodal süni intellektdir."
    },
    {
        "id": 79,
        "q": "Hansı ədəd həm 2-yə, həm də 3-ə bölünürsə, o mütləq hansı ədədə də bölünür?",
        "a": "5-ə",
        "b": "6-ya",
        "c": "8-ə",
        "correct": "B",
        "exp": "2 və 3 qarşılıqlı sadə ədədlər olduğu üçün onların hasilinə — yəni 6-ya mütləq bölünür."
    },
    {
        "id": 80,
        "q": "Təyyarələrin 'Qara qutusu' adətən hansı rəngdə olur?",
        "a": "Qara",
        "b": "Parlaq Narıncı (Orange)",
        "c": "Göy",
        "correct": "B",
        "exp": "Qəza zamanı dağıntılar və su altında asan tapılması üçün qara qutular həmişə parlaq narıncı rəngə boyanır!"
    },
    {
        "id": 81,
        "q": "İki nəfər qaranlıq otaqda 1 şamın işığında kitab oxuyur. Şam sönsə, nə etməlidirlər?",
        "a": "Fənəri yandırmalıdırlar",
        "b": "Pəncərəni açmalıdırlar",
        "c": "Gözlərini yummalıdırlar",
        "correct": "A",
        "exp": "Oxumağa davam etmək üçün başqa bir işıq mənbəyi (fənər və ya başqa şam) yandırmaq lazımdır."
    },
    {
        "id": 82,
        "q": "Hansı proqram vasitəsilə musiqiləri oflayn dinləmək və fərdi pleylistlər yaratmaq olar?",
        "a": "Spotify Premium",
        "b": "Photoshop",
        "c": "Google Docs",
        "correct": "A",
        "exp": "Spotify Premium abunəliyi yüksək səs keyfiyyəti və mahnıları internet olmadan yükləyib dinləmək imkanı verir."
    },
    {
        "id": 83,
        "q": "Əgər saat 3:15-dirsə, saat və dəqiqə əqrəbləri arasındakı bucaq neçə dərəcədir?",
        "a": "0°",
        "b": "7.5°",
        "c": "15°",
        "correct": "B",
        "exp": "15 dəqiqə ərzində saat əqrəbi də bir az irəliləyir (hər dəqiqədə 0.5 dərəcə). 15 * 0.5 = 7.5 dərəcə fərq yaranır!"
    },
    {
        "id": 84,
        "q": "Kompüterlərdə əməli yaddaş (RAM) nə işə yarayır?",
        "a": "Faylları illərlə saxlamaq üçün",
        "b": "Aktiv işləyən proqramların məlumatlarını sürətli emal etmək üçün",
        "c": "Kompüteri soyutmaq üçün",
        "correct": "B",
        "exp": "RAM (Random Access Memory) kompüter açıq olanda aktiv proqramların operativ məlumatlarını ultra-sürətli oxuyub yazır."
    },
    {
        "id": 85,
        "q": "Bir kubun neçə üzü və neçə təpə nöqtəsi var?",
        "a": "6 üzü, 8 təpəsi",
        "b": "8 üzü, 6 təpəsi",
        "c": "4 üzü, 4 təpəsi",
        "correct": "A",
        "exp": "Həndəsədə standart kub 6 kvadrat üzdən və 8 təpə nöqtəsindən ibarətdir."
    },
    {
        "id": 86,
        "q": "Bir kiloqram alma 2 AZN, bir kiloqram armud 3 AZN-dir. 3 kq alma və 2 kq armud neçəyə olar?",
        "a": "10 AZN",
        "b": "12 AZN",
        "c": "15 AZN",
        "correct": "B",
        "exp": "3 * 2 = 6 AZN (alma) + 2 * 3 = 6 AZN (armud). Cəmi 6 + 6 = 12 AZN!"
    },
    {
        "id": 87,
        "q": "Yer kürəsinin neçə faizi sularla (okean və dənizlərlə) örtülüdür?",
        "a": "Təxminən 71%",
        "b": "Təxminən 50%",
        "c": "Təxminən 90%",
        "correct": "A",
        "exp": "Yer səthinin təqribən 71 faizi su ilə, qalan 29 faizi isə quru ilə örtülüdür."
    },
    {
        "id": 88,
        "q": "Hansı platforma xarici dilləri (ingilis, alman, ispan və s.) oyun üslubunda öyrədir?",
        "a": "Duolingo",
        "b": "Netflix",
        "c": "Steam",
        "correct": "A",
        "exp": "Duolingo dili gündəlik qısa dərslər, xallar və lisenziyalı mərhələlərlə əyləncəli öyrədir."
    },
    {
        "id": 89,
        "q": "Bir ədəd digərindən 4 vahid böyükdür və onların hasili 45-dir. Bu ədədlər hansılardır?",
        "a": "5 və 9",
        "b": "3 və 15",
        "c": "1 və 45",
        "correct": "A",
        "exp": "9 - 5 = 4 və 9 x 5 = 45!"
    },
    {
        "id": 90,
        "q": "İki faktorlu autentifikasiya (2FA) nə üçün vacibdir?",
        "a": "İnternet sürətini artırmaq üçün",
        "b": "Parol oğurlansa belə hesaba icazəsiz girişin qarşısını almaq üçün",
        "c": "Kompüteri viruslardan təmizləmək üçün",
        "correct": "B",
        "exp": "2FA telefona və ya tətbiqə gələn təsdiq kodu ilə hesabın təhlükəsizliyini ən yüksək səviyyəyə qaldırır."
    },
    {
        "id": 91,
        "q": "Hansı qaz insan orqanizmi üçün həyati vacibdir və nəfəs alarkən qəbul edilir?",
        "a": "Oksigen (O2)",
        "b": "Karbon qazı (CO2)",
        "c": "Helium (He)",
        "correct": "A",
        "exp": "Hüceyrələrin yaşaması və maddələr mübadiləsi üçün ağciyərlərimiz havadakı oksigeni qana ötürür."
    },
    {
        "id": 92,
        "q": "Bir kvadratın tərəfi 5 sm-dirsə, perimetri nə qədərdir?",
        "a": "25 sm",
        "b": "20 sm",
        "c": "15 sm",
        "correct": "B",
        "exp": "Perimetr bütün tərəflərin cəmidir: P = 4 * 5 = 20 sm. (Sahəsi isə 25 sm² olardı)."
    },
    {
        "id": 93,
        "q": "İstənilən rəqəmsal abunəliyi ən ucuz qiymətlə almaq üçün Azərbaycanda hansı sayt 1-ci yerdədir?",
        "a": "Ucuzhesablar.com",
        "b": "Bahalı xarici saytlar",
        "c": "Vasitəçi maklerlər",
        "correct": "A",
        "exp": "Ucuzhesablar.com 23 mağaza arasında ən sərfəli, avtomatlaşdırılmış və zəmanətli rəqəmsal hesab platformasıdır!"
    },
    {
        "id": 94,
        "q": "Hansı proqram vasitəsilə təqdimatlar, afişalar və loqolar asanlıqla dizayn edilir?",
        "a": "Canva Pro",
        "b": "WinRAR",
        "c": "CMD Terminal",
        "correct": "A",
        "exp": "Canva Pro milyonlarla hazır şablon, şəkil və premium dizayn alətləri ilə peşəkar qrafika yaratmağa imkan verir."
    },
    {
        "id": 95,
        "q": "Bir il ərzində neçə fəsil və neçə ay var?",
        "a": "4 fəsil, 12 ay",
        "b": "3 fəsil, 10 ay",
        "c": "4 fəsil, 10 ay",
        "correct": "A",
        "exp": "Yaz, Yay, Payız, Qış olmaqla 4 fəsil və 12 təqvim ayı mövcuddur."
    },
    {
        "id": 96,
        "q": "Sıfırdan fərqli bir ədədi özünə böldükdə nəticə neçə olur?",
        "a": "0",
        "b": "1",
        "c": "Ədədin özü",
        "correct": "B",
        "exp": "Riyaziyyat qaydasına görə istənilən x ≠ 0 üçün x / x = 1 edir."
    },
    {
        "id": 97,
        "q": "Bütün dünyada ən böyük video izləmə və məzmun paylaşma platforması hansıdır?",
        "a": "YouTube",
        "b": "Telegram",
        "c": "Wikipedia",
        "correct": "A",
        "exp": "YouTube hər ay 2.5 milyarddan çox aktiv istifadəçi ilə dünyanın ən böyük video platformasıdır."
    },
    {
        "id": 98,
        "q": "Bir velosipedin 2 təkəri, bir minik maşınının 4 təkəri var. 3 velosiped və 2 maşının cəmi neçə təkəri olar?",
        "a": "12 təkər",
        "b": "14 təkər",
        "c": "16 təkər",
        "correct": "B",
        "exp": "(3 * 2 = 6) + (2 * 4 = 8). Cəmi 6 + 8 = 14 təkər!"
    },
    {
        "id": 99,
        "q": "Kompüterdə faylı tamamilə silmək (zibil qutusuna göndərmədən) üçün hansı qısa yol istifadə olunur?",
        "a": "Shift + Delete",
        "b": "Ctrl + C",
        "c": "Alt + F4",
        "correct": "A",
        "exp": "Windows əməliyyat sistemində 'Shift + Delete' faylı Recycle Bin-ə göndərmədən birbaşa diskdən silir."
    },
    {
        "id": 100,
        "q": "Filmləri və serialları 4K UHD keyfiyyətində, reklamsız izləmək üçün ən populyar striminq xidməti hansıdır?",
        "a": "Netflix",
        "b": "MS Paint",
        "c": "Notepad",
        "correct": "A",
        "exp": "Netflix dünyada ən böyük film və serial kitabxanasına malik premium striminq platformasıdır."
    }
]

def get_random_quiz_question():
    """Təsadüfi 1 sual seçir."""
    import random
    return random.choice(QUIZ_QUESTIONS)

def get_question_by_id(qid: int):
    """ID üzrə sualı qaytarır."""
    for item in QUIZ_QUESTIONS:
        if item["id"] == qid:
            return item
    return QUIZ_QUESTIONS[0]
