package com.wifihacker.pro;

import android.Manifest;
import android.content.pm.PackageManager;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private WebView webView;
    private WifiManager wifiManager;
    private List<String> passwordList = new ArrayList<>();
    private List<ScanResult> scanResults = new ArrayList<>();
    private Handler handler = new Handler(Looper.getMainLooper());
    private static final int PERMISSION_REQUEST = 100;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        wifiManager = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
        webView = findViewById(R.id.webView);
        
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setAllowFileAccess(true);
        webView.getSettings().setAllowContentAccess(true);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                // ربط Bridge بعد تحميل الصفحة
                view.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
            }
        });
        
        checkPermissions();
        webView.loadUrl("file:///android_asset/index.html");
    }

    private void checkPermissions() {
        String[] perms = {
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        };
        List<String> need = new ArrayList<>();
        for (String p : perms) {
            if (ContextCompat.checkSelfPermission(this, p) != PackageManager.PERMISSION_GRANTED) {
                need.add(p);
            }
        }
        if (!need.isEmpty()) {
            ActivityCompat.requestPermissions(this, need.toArray(new String[0]), PERMISSION_REQUEST);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST) {
            for (int r : grantResults) {
                if (r != PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "⚠️ بعض الصلاحيات مطلوبة", Toast.LENGTH_LONG).show();
                    return;
                }
            }
        }
    }

    // ============================================
    // 🔥 JavaScript Bridge
    // ============================================
    public class AndroidBridge {
        @JavascriptInterface
        public void toggleWiFi() {
            wifiManager.setWifiEnabled(!wifiManager.isWifiEnabled());
        }

        @JavascriptInterface
        public void scanNetworks() {
            if (!wifiManager.isWifiEnabled()) {
                handler.post(() -> webView.loadUrl("javascript:showToast('⚠️ يرجى تشغيل الواي فاي أولاً')"));
                return;
            }
            handler.post(() -> webView.loadUrl("javascript:document.getElementById('statusText').innerHTML = '⏳ جاري المسح...'"));
            
            wifiManager.startScan();
            scanResults = wifiManager.getScanResults();
            
            List<NetworkInfo> networks = new ArrayList<>();
            for (ScanResult r : scanResults) {
                String ssid = r.SSID != null && !r.SSID.isEmpty() ? r.SSID : "<مخفي>";
                String bssid = r.BSSID;
                int signal = WifiManager.calculateSignalLevel(r.level, 100);
                String encryption = r.capabilities.contains("WPA3") ? "WPA3" :
                                    r.capabilities.contains("WPA2") ? "WPA2" :
                                    r.capabilities.contains("WPA") ? "WPA" :
                                    r.capabilities.contains("WEP") ? "WEP" : "Open";
                networks.add(new NetworkInfo(ssid, bssid, signal, encryption));
            }
            
            String json = new com.google.gson.Gson().toJson(networks);
            handler.post(() -> webView.loadUrl("javascript:receiveRealNetworks('" + json + "')"));
        }

        @JavascriptInterface
        public void loadPasswordFile() {
            // فتح مستكشف الملفات عبر Intent
            android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_GET_CONTENT);
            intent.setType("text/plain");
            startActivityForResult(android.content.Intent.createChooser(intent, "اختر ملف الباسوردات"), 200);
        }

        @JavascriptInterface
        public void startAutoConnect(String passwordsJson) {
            // استقبال كلمات المرور من JS
            try {
                passwordList = new com.google.gson.Gson().fromJson(passwordsJson, new com.google.gson.reflect.TypeToken<List<String>>(){}.getType());
            } catch (Exception e) {
                passwordList = new ArrayList<>();
            }
            
            if (passwordList.isEmpty() || scanResults.isEmpty()) {
                handler.post(() -> webView.loadUrl("javascript:showToast('⚠️ بيانات ناقصة')"));
                return;
            }

            handler.post(() -> webView.loadUrl("javascript:document.getElementById('attackProgress').style.display='block'"));
            
            new Thread(() -> {
                for (ScanResult r : scanResults) {
                    String ssid = r.SSID != null ? r.SSID : "<مخفي>";
                    String bssid = r.BSSID;
                    
                    // محاولة الاتصال بكل كلمة مرور
                    for (String pwd : passwordList) {
                        boolean success = tryConnect(bssid, pwd);
                        if (success) {
                            String result = "{"success":true,"ssid":"" + ssid + "","password":"" + pwd + ""}";
                            handler.post(() -> webView.loadUrl("javascript:receiveCrackResult('" + result + "')"));
                            return;
                        }
                    }
                }
                // فشل
                String result = "{"success":false}";
                handler.post(() -> webView.loadUrl("javascript:receiveCrackResult('" + result + "')"));
            }).start();
        }

        private boolean tryConnect(String bssid, String password) {
            // تنفيذ الاتصال الفعلي (يحتاج إلى WifiConfiguration)
            // يتم إرجاع true أو false بناءً على نجاح الاتصال
            return false; // placeholder
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, android.content.Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 200 && resultCode == RESULT_OK && data != null) {
            try {
                InputStream is = getContentResolver().openInputStream(data.getData());
                BufferedReader br = new BufferedReader(new InputStreamReader(is));
                passwordList.clear();
                String line;
                while ((line = br.readLine()) != null) {
                    if (line.trim().length() > 0) passwordList.add(line.trim());
                }
                br.close();
                String json = new com.google.gson.Gson().toJson(passwordList);
                handler.post(() -> webView.loadUrl("javascript:receivePasswordList('" + json + "')"));
            } catch (Exception e) {
                handler.post(() -> webView.loadUrl("javascript:showToast('❌ خطأ في القراءة')"));
            }
        }
    }

    // ============================================
    // NetworkInfo Class
    // ============================================
    public class NetworkInfo {
        public String ssid, bssid, encryption;
        public int signal;
        public NetworkInfo(String ssid, String bssid, int signal, String encryption) {
            this.ssid = ssid; this.bssid = bssid; this.signal = signal; this.encryption = encryption;
        }
    }
}