# Zeuniverse: Android Resources

Folder `res/` ini siap di-copy ke `app/src/main/res/`. Semua file di-generate dari logo kit lewat
`../build_android.py`. Kalau logo berubah, jalankan ulang `python build_kit.py kit` lalu `python build_android.py kit android`.

Sudah divalidasi dengan `aapt2 compile` dan `aapt2 link` (build-tools 36, android-37).

## Isi

| File | Fungsi |
|---|---|
| `mipmap-anydpi-v26/ic_launcher.xml`, `ic_launcher_round.xml` | Adaptive icon: background orange, foreground wajah Otan, monochrome untuk themed icon (Android 13+) |
| `drawable/ic_launcher_foreground.xml` | Wajah Otan di kanvas 108 dp, seluruhnya di dalam safe zone 66 dp, jadi aman untuk semua bentuk mask |
| `drawable/ic_launcher_monochrome.xml` | Siluet kepala satu warna, diwarnai otomatis oleh sistem |
| `values/ic_launcher_background.xml` | `#F5822A` |
| `mipmap-mdpi … xxxhdpi/ic_launcher(_round).png` | Ikon PNG untuk HP lama (API < 26): 48 / 72 / 96 / 144 / 192 px |
| `drawable/ic_stat_zeuniverse.xml` | Ikon notifikasi 24 dp, putih di atas transparan |
| `drawable/splash_icon.xml` | Ikon splash screen 288 dp, isinya muat di lingkaran 192 dp |
| `drawable/zeuniverse_*.xml` | Logo untuk dipakai di dalam aplikasi: icon, icon_small, head, icon_mono, horizontal, stacked, wordmark (masing-masing ada versi `_white`) |
| `drawable/otan_*.xml` | Ekspresi Otan: default, happy, wink, wow, astronaut |
| `values/zeuniverse_colors.xml` | `zeuniverse_orange`, `zeuniverse_fur_shade`, `zeuniverse_peach`, `zeuniverse_navy` |
| `../playstore/ic_launcher-playstore.png` | 512×512 untuk Google Play Console (bukan bagian dari `res/`) |

## 1. Pasang

1. **Hapus dulu ikon bawaan template Android Studio**, supaya tidak muncul error *Duplicate resources*:
   - `mipmap-*/ic_launcher.webp` dan `ic_launcher_round.webp`
   - `mipmap-anydpi-v26/ic_launcher*.xml`
   - `drawable/ic_launcher_foreground.xml` dan `drawable/ic_launcher_background.xml`
   - `values/ic_launcher_background.xml` (kalau ada)
2. Copy isi `res/` ke `app/src/main/res/`.
3. Pastikan `AndroidManifest.xml` sudah memakai ikon ini (biasanya sudah otomatis):
   ```xml
   <application
       android:icon="@mipmap/ic_launcher"
       android:roundIcon="@mipmap/ic_launcher_round" … >
   ```

## 2. Splash screen (Android 12+, dengan backport untuk versi lama)

`build.gradle.kts`:
```kotlin
implementation("androidx.core:core-splashscreen:1.0.1")
```

`res/values/themes.xml`:
```xml
<style name="Theme.Zeuniverse.Starting" parent="Theme.SplashScreen">
    <item name="windowSplashScreenBackground">@color/zeuniverse_orange</item>
    <item name="windowSplashScreenAnimatedIcon">@drawable/splash_icon</item>
    <item name="postSplashScreenTheme">@style/Theme.Zeuniverse</item>
</style>
```

Set `android:theme="@style/Theme.Zeuniverse.Starting"` di `<activity>` utama, lalu di `MainActivity`:
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    installSplashScreen()
    super.onCreate(savedInstanceState)
    …
}
```

## 3. Notifikasi

```kotlin
NotificationCompat.Builder(context, CHANNEL_ID)
    .setSmallIcon(R.drawable.ic_stat_zeuniverse)
    .setColor(ContextCompat.getColor(context, R.color.zeuniverse_orange))
    …
```

## 4. Jetpack Compose

```kotlin
val ZeuniverseOrange = Color(0xFFF5822A)
val ZeuniverseNavy   = Color(0xFF2B2862)

// header
Image(
    painter = painterResource(R.drawable.zeuniverse_horizontal),
    contentDescription = "Zeuniverse",
    modifier = Modifier.height(32.dp)
)

// ekspresi Otan sesuai state, misalnya jawaban benar atau salah
val otan = when (state) {
    Result.Correct -> R.drawable.otan_happy
    Result.Wrong   -> R.drawable.otan_wow
    else           -> R.drawable.otan_default
}
Image(painterResource(otan), contentDescription = "Otan", modifier = Modifier.size(96.dp))
```

Di layar gelap, pakai `zeuniverse_horizontal_white`. Ukuran di XML hanya ukuran default. Di Compose, ukurannya bebas diatur lewat `Modifier`.

## Catatan

- **`minSdk` sebaiknya 24 ke atas.** `zeuniverse_icon_mono` dan `ic_stat_zeuniverse` memakai lubang (`fillType="evenOdd"`), yang baru didukung sejak API 24. Di API 21–23, lubang mata dan mulut akan tertutup.
- Jangan pakai `zeuniverse_icon` sebagai foreground adaptive icon. Ikon itu sudah punya tile sendiri, jadi hasilnya akan jadi tile di dalam tile.
- Ikon Play Store harus kotak penuh, karena sudut membulatnya diterapkan otomatis oleh Google Play.
