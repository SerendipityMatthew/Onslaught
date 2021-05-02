package me.xuwanjin.onslaughtapp

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.thanosfisherman.wifiutils.WifiUtils
import com.thanosfisherman.wifiutils.wifiConnect.ConnectionErrorCode
import com.thanosfisherman.wifiutils.wifiConnect.ConnectionSuccessListener


class MainActivity : AppCompatActivity() {
    private lateinit var wifiSsid: EditText
    private lateinit var wifiPassword: EditText
    private lateinit var connectToWiFi: Button
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        wifiSsid = findViewById(R.id.wifi_ssid)
        wifiPassword = findViewById(R.id.wifi_password)
        connectToWiFi = findViewById(R.id.connect_to_wifi)

        connectToWiFi.setOnClickListener(object : View.OnClickListener {
            override fun onClick(v: View?) {
                connectToWiFi(wifiSsid.text.trim().toString(), wifiPassword.text.trim().toString())
            }
        })

    }

    private fun connectToWiFi(wifiSsid: String, wifiPassword: String) {
        if (wifiSsid.trim() == "") {
            return
        }
        if (wifiPassword.trim() == "") {
            return
        }
        WifiUtils.withContext(applicationContext)
                .connectWith(wifiSsid, wifiPassword)
                .setTimeout(10000)
                .onConnectionResult(object : ConnectionSuccessListener {
                    override fun success() {
                        Toast.makeText(this@MainActivity, "SUCCESS!", Toast.LENGTH_SHORT).show()
                    }

                    override fun failed(errorCode: ConnectionErrorCode) {
                        Toast.makeText(this@MainActivity, "EPIC FAIL!$errorCode", Toast.LENGTH_SHORT).show()
                    }
                })
                .start()
    }
}