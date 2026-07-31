---
description: "Küçük bir siteyi otuz beş dile çevirmenin gerçekte neleri bozduğu, bunların hangilerini kütüphane sizin için yakalayabilir ve hangilerini yakalayamaz."
---

# Tuzaklar

Bu site otuz beş dile çevrilmiştir ve bu dil sürümlerinin her biri, bu
belgelerin öğrettiği döngü çalıştırılarak üretilmiştir. Sektör ölçülerine göre
bu küçük bir derlemdir ve yine de i18n'i göründüğünden zor kılan tuzakların
çoğuna düşmeye yetmiştir.

Aşağıdaki her bölüm, burada gerçekten ters giden bir şeydir: o an nasıl
göründüğü ve kütüphanenin sizin için denetlediği şeyle sizin muhakemenize
kalan şey arasındaki çizginin nereye düştüğü.

## Bir değişkeni yeniden adlandırmak bir cümleyi yeniden çevirtir { #renaming-a-variable-retranslates-a-sentence }

msgid katalog anahtarıdır ve interpolasyona giren bir ad onun *içindedir*.
Bir sabiti modül kapsamına taşıyıp Python biçem alışkanlığının istediği gibi
büyük harfe çevirmek — `author`'ı `AUTHOR` yapmak —
`Copyright © 2026 {author} · MIT License` mesajını hiçbir kataloğun daha önce
görmediği bir mesaja dönüştürdü. O satırın her dildeki her çevirisi, okurun
görebileceği hiçbir şeyi değiştirmeyen bir yeniden adlandırma uğruna fuzzy
çevrimine geri gidecekti.

Kütüphane sizi durdurmaz: iki yazım da geçerli birer yer tutucu adıdır.
Yaptığı şey, o adı korunmaya *değer* kılmaktır — bir interpolasyon
[yalın bir ad](internals.md#from-template-to-msgid) olmak zorundadır;
dolayısıyla katalog anahtarındaki şey, bir çevirmenin okuyabileceği bir
kelimedir, bir ifade değil.

Bunun aynadaki hali yapısı gereği güvenlidir. Dönüşümler ve biçim belirtimleri
msgid'nin parçası değildir; bu yüzden `{amount:,.2f}` biçimini `{amount:,.0f}`
olarak sıkılaştırmak hiçbir anahtarı değiştirmez ve hiçbir yerde hiçbir
çeviriyi geçersizleştirmez.

## `nplurals=2`, iki farklı dizgi demek değildir { #nplurals-2-does-not-mean-two-different-strings }

Türkçe, Macarca, Farsça ve Bengalce iki çoğul biçim bildirir ve dördünde de
sayılan bir mesajın iki biçimi meşru olarak *aynı dizgidir* — ad bir sayıdan
sonra tekil kaldığı için `{n} sayfa` hem bir sayfa hem on sayfa için doğrudur.
Yinelemeyi "düzelten" bir gözden geçiren, çeviriyi bozar.

Ters yöndeki hata da bir o kadar kolaydır. Letoncanın üçüncü biçimi
**yalnızca sıfır** için vardır; Slovencenin ikincisi bir **ikil**dir, tam
olarak iki içindir; Romencenin son biçimi, ilk ikisinde bulunmaması gereken
`de` kelimesini gerektirir. Bu yuvaları bir tekil ve bir çoğulla doldurmak,
yalnızca kimsenin denemediği sayılar için yanlış olan bir katalog üretir.

Daha kötüsü, yuvaların *sırası* anlamsal değildir. Galce beş biçimini öyle
numaralar ki `msgstr[0]` genel durumdur ve `msgstr[1]` tekildir. Onları akla
ilk gelen sırayla doldurmak, tekili sayısız her mesajın bulacağı yere koyar.

Kütüphane bunların hiçbirini üstlenmez ve mesele de budur: hedef dilin çoğul
kuralı kendi kataloğunun başlığında yaşar ve
[birleşim/kesişim kuralı](spec.md) bir çevirinin kaynaktan daha çok ya da daha
az biçimi olmasına izin verir. Denetlediği şey, dili bilmeden
denetleyebileceği tek şeydir — her biçimin ihtiyaç duyduğu yer tutucuları
koruduğu.

## İki biçim bir sebeple birebir aynı olabilir { #two-forms-can-be-identical-for-a-reason }

İrlandacanın beş çoğul biçimi vardır ve bu sitenin derleme raporunda bunların
birkaçı aynı yazılır. Bu bir kopyala-yapıştır kazası değildir: *leathanach*
`l` ile başlar ve İrlandaca sayıların tetiklediği iki baş mutasyonun ikisi de
`l` üzerinde yazıya dökülmez. Biçimler yine de gerçek iş görür — gövde
*leathanach* ile *leathanaigh* arasında değişir ve ondan büyük sayılar tekile
döner — ama "sayfa" anlamına gelen hiçbir ad bu karşıtlığı göstermezdi.

Yinelenen biçimleri şüpheli diye işaretleyen her denetim, doğru İrlandacayı
işaretleyecektir. Bunun tek gözden geçireni, dili bilen bir insandır.

## Bir mesaj yalnızca tek bir sayıyla uyuşabilir { #a-message-can-only-agree-with-one-count }

Bu sitenin derleme raporu, kaç sayfanın render edildiğini ve bunun ne kadar
sürdüğünü söyler. Bunu "Rendered {n} pages in {seconds} seconds" diye yazmak
zararsız görünür ve çevrilebilir değildir: gettext tek bir sayıdan tek bir
biçim seçer ve o sayı `n`'dir. *seconds* kelimesinin, çoğul düzeneğinin hiç
görmediği bir sayıyla uyuşması gerekirdi.

Çözüm, ikinci niceliği bir kelime yerine bir birim simgesi yapmaktır; birim
simgelerinin kendileri de yerelleştirilir: bu sitenin katalogları `s`, `с`,
`ث`, `שנ׳` ve `mp` taşır ve Fransızca, İspanyolca ve İsveççe dizgi geleneği,
İngilizcenin istemediği bir boşluğu simgeden önce ister. Bunların hiçbiri
kütüphanenin işi değildir — ama bir mesajın *iki* uyuşmaya ihtiyaç duyduğunu
fark etmek işin bir parçasıdır ve bunun tek aracı, mesajı başka türlü
yazmaktır.

## Bir İngilizce cümleyi düzenlemek yabancı dil bilgisini düzenler { #editing-an-english-sentence-edits-foreign-grammar }

Ana sayfa eskiden "all ten language editions" diyordu. Sayının kaldırılması —
tek kelimelik bir İngilizce düzenleme; sayı sürekli bayatladığı için yapıldı —
çoğul bir özneyi tekile çevirdi. İspanyolca, İtalyanca, Portekizce, Rusça,
Ukraynaca, Yunanca, Felemenkçe ve İbranice sürümlerin hepsinde yüklemin uyumu
yeniden kurulmak zorunda kaldı; birkaçında ortacın da değişmesi gerekti.

İngilizcede önemsiz okunan bir kaynak düzenlemesi, akışın aşağısında önemsiz
değildir. `pybabel update`'in yaptığı şey olan fuzzy işaretleme, her çevirmene
bunu fark etme şansını veren düzenektir.

## Görülemeyen farklar her kopyala-yapıştırdan sağ çıkar { #invisible-differences-survive-every-copy-paste }

Kılavuz, `(nаme)` içeren bir tanıyı alıntılar — bilerek konmuş bir kaçış,
çünkü adlandırdığı karakter, hiçbir okurun Latin olanından ayırt edemeyeceği
bir Kiril `а` harfidir. Bu sitenin çevirmenleri o kaçışı **beş ayrı kez**, beş
farklı dilde, karakterin kendisine dönüştürdü ve her seferinde doğru görünen,
yanlış olan bir sayfa üretti.

Bunu kütüphane gerçekten yakalar ve tanıların bu biçimde tasarlanmış olmasının
sebebi de budur: harfleri yazı sistemlerini karıştıran bir yer tutucu
[iki kez raporlanır](internals.md#diagnostics-are-part-of-the-design) — bir
kez okunur biçimde, bir kez kaçışlanmış olarak; çünkü ikisini birbirinden
ayıran tek yazım, kaçışlanmış biçimdir. Ayraçların içindeki bölünmesiz bir
boşluk da aynı sebeple kod noktasıyla yazdırılır. Katalog denetleyicisi,
mesajı sevk edilebilmesinden önce geri çevirir.

## Boş olmaması çevrilmiş olması demek değildir { #non-empty-is-not-translated }

msgid'leri msgstr'lerine kopyalanarak iskeleti kurulmuş bir katalog, her naif
denetimden geçer: hiçbir şey boş değildir, hiçbir şey fuzzy değildir, mesaj
kümesi tam olarak uyar. Bu sitenin bir dil sürümü birkaç saat boyunca böyle
sevk edildi. Bir başka sürümün, İngilizce kaynağın bayt bayt kopyası olan
sekiz sayfası da öyle — bu, aralarındaki kod bloklarını karşılaştıran bir
denetimden geçer, çünkü onlar aynı dosyadır.

Bunların ikisi de bir çeviri kütüphanesinin görebileceği şeyler değildir.
İkisini de, bir kez akla geldikten sonra, sınamak ucuzdur: kaynakla
karşılaştırın ve bir fark isteyin.

## Çevrilen tek şey katalog değildir { #the-catalog-is-not-the-only-translated-thing }

Buradaki iki hatanın gettext'le hiçbir ilgisi yoktu.

Bir başlığı çevirmek, ondan üretilen çapayı değiştirir; böylece o bölüme giren
her sayfalar arası bağlantı bozulur — sessizce ve yalnızca o dilde. Bu site,
her başlıkta İngilizce çapayı sabitler ve bir test, beklenen listeyi İngilizce
sayfadan türetir.

Site üreticisi de arayüz çevirilerini altmış sekiz dil için sevk eder; bu
diller arasında Svahili ve İrlandaca yoktur. Biri yoksa derleme İngilizceye
düşerek idare etmez; şablon include'u başarısız olur ve o dil sürümü hiç
derlenemez. Bu deponun kendi dosyalarından ikisi, o boşluğu doldurmak için
vardır.

## Sizin araçlarınızın da hataları var { #your-tools-have-bugs-too }

Bu belgelerin bayat katalogları yakalamak için önerdiği CI adımı,
`pybabel update --check`, `pgettext` ya da `npgettext` kullanan hiçbir projede
bu işi yapamaz — `msgctxt` taşıyan her kataloğu, her koşuda güncel değil diye
raporlar; çünkü karşılaştırmanın mesajları arama biçiminde bir hata vardır.
Burada, kullanılmaya çalışılırken bulundu, üst akışa bildirildi ve
[geçici çözümüyle birlikte tam olarak anlatıldı](workflow.md#what-ci-gates).

Genel ders, rahatsız edici olanıdır: hep kırmızı yanan bir kapı, hiç kapı
olmamasından kötüdür; çünkü ekip onu kapatır. CI denetiminizin başarısız
olmasına güvenmeden önce, gerçekten geçebildiğini doğrulayın.

## Kütüphane tek cümleyle ne işe yarar { #what-the-library-is-for-in-one-line }

Bu sayfanın çoğu, hiçbir aracın devralamayacağı bir muhakemedir. Bir aracın
*yapabileceği* şey, bir çevirinin, çevirdiği cümlenin yapısını
değiştiremeyeceğini güvence altına almaktır — bir değeri düşüremez, olmayan
birini uyduramaz, birini yeniden biçimlendiremez ya da nesnelerinize uzanamaz
— ve bunu, düzeltmek zorunda kalan kişinin üzerine harekete geçebileceği bir
cümleyle söyleyebilmektir. Bu kütüphanenin verdiği sözün tamamı budur; bu
sitenin geri kalanı da o sözün nasıl tutulduğudur.
