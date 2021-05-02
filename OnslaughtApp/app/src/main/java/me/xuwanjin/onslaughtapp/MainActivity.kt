package me.xuwanjin.onslaughtapp

import android.Manifest
import android.annotation.SuppressLint
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.net.*
import android.net.ConnectivityManager.NetworkCallback
import android.net.wifi.*
import android.net.wifi.hotspot2.PasspointConfiguration
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.thanosfisherman.wifiutils.WifiUtils
import com.thanosfisherman.wifiutils.wifiConnect.ConnectionErrorCode
import com.thanosfisherman.wifiutils.wifiConnect.ConnectionSuccessListener
import me.xuwanjin.onslaughtapp.Constants.*


class MainActivity : AppCompatActivity() {
    companion object {
        const val TAG = "MainActivity"
    }

    private val oldWays: Boolean = true
    private lateinit var wifiSsid: EditText
    private lateinit var wifiPassword: EditText
    private lateinit var connectToWiFi: Button
    private var mWifiList: ArrayList<ScanResult> = ArrayList<ScanResult>()
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
        if (oldWays) {
            scanWifiInfo()
        } else {
            WifiUtils.withContext(applicationContext)
                .connectWith(wifiSsid, wifiPassword)
                .setTimeout(10000)
                .onConnectionResult(object : ConnectionSuccessListener {
                    override fun success() {
                        Toast.makeText(this@MainActivity, "SUCCESS!", Toast.LENGTH_SHORT).show()
                    }

                    override fun failed(errorCode: ConnectionErrorCode) {
                        Toast.makeText(
                            this@MainActivity,
                            "EPIC FAIL!$errorCode",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                })
                .start()
        }

    }

    private fun scanWifiInfo() {
        @SuppressLint("WifiManagerLeak") val mWifiManager = getSystemService(WIFI_SERVICE) as WifiManager
        mWifiManager.isWifiEnabled = true
        mWifiManager.startScan()
        mWifiList.clear()
        mWifiList = mWifiManager.scanResults as ArrayList<ScanResult>
        Log.d(TAG, "scanWifiInfo: mWifiList.size() = " + mWifiList.size)
        if (mWifiList != null && mWifiList.size > 0) {
            for (scanResult in mWifiList) {
                Log.d(TAG, "scanWifiInfo: scanResult.SSID = " + scanResult.SSID)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    connectWifiAndroidQSaveNetwork(wifiSsid.text.trim().toString(), wifiPassword.text.trim().toString())
                } else {
                    connectWifi(
                        wifiSsid.text.trim().toString(),
                        wifiPassword.text.trim().toString(),
                        WIFI_ENCRYPT_WPA
                    )
                }
                return
            }
        }
    }

    @RequiresApi(Build.VERSION_CODES.Q)
    fun connectWifiAndroidQSuggestions(ssid:String, password:String) {
        val suggestion2 = WifiNetworkSuggestion.Builder()
            .setSsid(ssid)
            .setWpa2Passphrase(password)
            .setIsAppInteractionRequired(true) // Optional (Needs location permission)
            .build()

        val suggestionsList = listOf( suggestion2)

        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager;
        val status = wifiManager.addNetworkSuggestions(suggestionsList);
        if (status != WifiManager.STATUS_NETWORK_SUGGESTIONS_SUCCESS) {
            // do error handling here
        }
    }

    @RequiresApi(api = Build.VERSION_CODES.Q)
    fun connectWifiAndroidQ(ssid: String?, password: String?) {
        val specifier: NetworkSpecifier = WifiNetworkSpecifier.Builder()
            .setSsid(ssid!!)
            .setWpa2Passphrase(password!!)
            .build()
        val request = NetworkRequest.Builder()
            .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addCapability(NetworkCapabilities.NET_CAPABILITY_NOT_RESTRICTED)
            .removeCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .setNetworkSpecifier(specifier)
            .build()
        val connectivityManager =
            applicationContext.getSystemService(CONNECTIVITY_SERVICE) as ConnectivityManager
        val networkCallback: NetworkCallback = object : NetworkCallback() {
            override fun onAvailable(network: Network) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    connectivityManager.bindProcessToNetwork(network)
                } else {
                    ConnectivityManager.setProcessDefaultNetwork(network)
                }

            }

            override fun onUnavailable() {
                Log.d(TAG, "connectWifiAndroidQ: onUnavailable: ")
                Toast.makeText(applicationContext, " network is not available", Toast.LENGTH_SHORT)
                    .show()
            }
        }
        connectivityManager.requestNetwork(request, networkCallback)
    }

    /**
     * 连接wifi
     *
     * @param targetSsid wifi的SSID
     * @param targetPsd  密码
     * @param enc        加密类型, 特别注意这个参数是否正确
     */
    @SuppressLint("WifiManagerLeak")
    fun connectWifi(targetSsid: String, targetPsd: String, enc: String?) {
        Log.d(TAG, "connectWifi: ")
        // 1、注意热点和密码均包含引号，此处需要需要转义引号
        val ssid = "\"" + targetSsid + "\""
        val psd = "\"" + targetPsd + "\""

        //2、配置wifi信息
        val conf = WifiConfiguration()
        conf.SSID = ssid
        when (enc) {
            WIFI_ENCRYPT_WEP -> {
                // 加密类型为WEP
                conf.wepKeys[0] = psd
                conf.wepTxKeyIndex = 0
                conf.allowedKeyManagement.set(WifiConfiguration.KeyMgmt.NONE)
                conf.allowedGroupCiphers.set(WifiConfiguration.GroupCipher.WEP40)
            }
            WIFI_ENCRYPT_WPA ->                 // 加密类型为WPA
                conf.preSharedKey = psd
            WIFI_ENCRYPT_OPEN ->                 //开放网络
                conf.allowedKeyManagement.set(WifiConfiguration.KeyMgmt.NONE)
        }
        //3、链接wifi
        val wifiManager = applicationContext.getSystemService(WIFI_SERVICE) as WifiManager
        wifiManager.addNetwork(conf)
        if (ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
            return
        }
        val list = wifiManager.configuredNetworks
        Log.d(TAG, "connectWifi: list = " + list.size)
        for (wifiConfiguration in list) {
            Log.d(TAG, "connectWifi: wifiConfiguration.SSID = " + wifiConfiguration.SSID)
            if (wifiConfiguration.SSID != null && wifiConfiguration.SSID == ssid) {
                wifiManager.disconnect()
                wifiManager.enableNetwork(wifiConfiguration.networkId, true)
                val isConnected = wifiManager.reconnect()
                Log.d(TAG, "connectWifi: isConnected = $isConnected")
                break
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (resultCode == RESULT_OK) {
            // user agreed to save configurations: still need to check individual results
            if (data != null && data.hasExtra(Settings.EXTRA_WIFI_NETWORK_RESULT_LIST)) {
                for (code in data.getIntegerArrayListExtra(Settings.EXTRA_WIFI_NETWORK_RESULT_LIST)!!) {
                    when (code) {
                        Settings.ADD_WIFI_RESULT_SUCCESS -> {

                        }
                        Settings.ADD_WIFI_RESULT_ADD_OR_UPDATE_FAILED -> {

                        }
                        Settings.ADD_WIFI_RESULT_ALREADY_EXISTS -> {

                        }
                        else -> {

                        }
                    }
                }
            }
        } else {
            // User refused to save configurations
        }
    }

    /**
     *
     */
    @RequiresApi(Build.VERSION_CODES.Q)
    fun connectWifiAndroidQSaveNetwork(ssid:String, password:String) {
        val suggestions = ArrayList<WifiNetworkSuggestion>()

        // WPA2 configuration
        suggestions.add(
            WifiNetworkSuggestion.Builder()
                .setSsid(ssid)
                .setWpa2Passphrase(password)
                .build()
        )

        // Create intent
        val bundle = Bundle()
        bundle.putParcelableArrayList(Settings.EXTRA_WIFI_NETWORK_LIST, suggestions)
        val intent = Intent(Settings.ACTION_WIFI_ADD_NETWORKS)
        intent.putExtras(bundle)

        // Launch intent
        startActivityForResult(intent, 0)
    }
}

