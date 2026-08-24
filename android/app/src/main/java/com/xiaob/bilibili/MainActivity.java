package com.xiaob.bilibili;

import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        
        // 配置 WebView
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setLoadWithOverviewMode(true);
        webView.getSettings().setUseWideViewPort(true);
        
        // 设置 WebViewClient 拦截导航
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                
                // 只允许 bilibili.com 及其子域名
                if (url.contains("bilibili.com") || 
                    url.contains("hdslb.com") || 
                    url.contains("bilivideo.com") ||
                    url.contains("acgvideo.com") ||
                    url.contains("biliapi.net") ||
                    url.contains("biliimg.com")) {
                    return false; // 允许加载
                } else {
                    // 阻止非 Bilibili 域名，返回首页
                    view.loadUrl("https://www.bilibili.com");
                    return true;
                }
            }
        });
        
        // 加载 Bilibili 首页
        webView.loadUrl("https://www.bilibili.com");
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
