package com.example.sofie;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.os.AsyncTask;
import android.os.IBinder;
import android.util.Log;
import android.widget.Toast;


import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ServerSocket;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import com.google.gson.GsonBuilder;

import static android.content.ContentValues.TAG;
import static com.example.sofie.MainActivity.NSD_DEVICES;


public class NSD extends Service {

    private static final String TAG = "NSD::";

    public NsdManager NSDMANAGER;
    public NsdManager.RegistrationListener REGISTRATIONLISTENER;
    public NsdManager.DiscoveryListener DISCOVERYLISTENER;

    public String SERVICENAME;
    public int LOCALPORT;
    public String ID;

    public ServerSocket SERVERSOCKET;

    //public static ArrayList<NsdServiceInfo> NSD_DEVICES;

    public static int a = 1;

    public NSD() {
    }

    @Override
    public IBinder onBind(Intent intent) {
        throw new UnsupportedOperationException("Not yet implemented");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {

        // oi9juID = android.provider.Settings.Secure.getString(this.getContentResolver(), android.provider.Settings.Secure.ANDROID_ID);
        NSDMANAGER = (NsdManager) getApplicationContext().getSystemService(Context.NSD_SERVICE);

        initializeDiscoveryListener();
        //initializeRegistrationListener();
        initializeServerSocket();
        this.discoverServices();

        //this.registerService(LOCALPORT);
        Toast.makeText(this, "NSD Started",Toast.LENGTH_SHORT).show();

        return super.onStartCommand(intent, flags, startId);
    }


    public void discoverServices() {
        NSDMANAGER.discoverServices("_webthing._tcp.", NsdManager.PROTOCOL_DNS_SD, DISCOVERYLISTENER);
    }


    public void initializeServerSocket() {
        try {
            SERVERSOCKET = new ServerSocket(0);
            LOCALPORT = SERVERSOCKET.getLocalPort();
        }
        catch (IOException ie){
            Log.d(TAG, "initializeServerSocket: Socket Error");
        }

    }

    public void initializeDiscoveryListener() {
        DISCOVERYLISTENER = new NsdManager.DiscoveryListener() {
            @Override
            public void onDiscoveryStarted(String regType) {
                Log.d(TAG, "Service discovery started");
            }

            @Override
            public void onServiceFound(NsdServiceInfo service) {
                Log.d(TAG, "Service discovery success" + service);
                if (!service.getServiceType().equals("_webthing._tcp.")) {
                    Log.d(TAG, "Unknown Service Type: " + service.getServiceType());
                } else if (service.getServiceName().equals(SERVICENAME)) {
                    Log.d(TAG, "Same machine: " + SERVICENAME);
                } else {
                    NSDMANAGER.resolveService(service, new NsdManager.ResolveListener(){
                        @Override
                        public void onResolveFailed(NsdServiceInfo serviceInfo, int errorCode) {
                            Log.d(TAG, "Resolve failed" + errorCode);
                        }

                        @Override
                        public void onServiceResolved(NsdServiceInfo serviceInfo) {
                            Log.d(TAG, "Resolve Succeeded. " + serviceInfo);
                            String URL = "http://" + serviceInfo.getHost().getHostAddress()+ ":5000/api/iBeacon";

                            beaconTask beacon = new beaconTask();
                            beacon.execute(URL);
                            if (serviceInfo.getServiceName().equals(SERVICENAME)) {
                                Log.d(TAG, "Same IP.");
                                return;
                            }
                            if (!NSD_DEVICES.contains(serviceInfo)){
                                NSD_DEVICES.add(serviceInfo);
                                MainActivity.adapter.add(serviceInfo);
                            }

                        }
                    });
                }
            }

            @Override
            public void onServiceLost(NsdServiceInfo service) {
                Log.d(TAG, "Service lost" + service);
            }

            @Override
            public void onDiscoveryStopped(String serviceType) {
                Log.d(TAG, "Discovery stopped: " + serviceType);
            }

            @Override
            public void onStartDiscoveryFailed(String serviceType, int errorCode) {
                Log.d(TAG, "Discovery failed: Error code:" + errorCode);
                NSDMANAGER.stopServiceDiscovery(this);
            }

            @Override
            public void onStopDiscoveryFailed(String serviceType, int errorCode) {
                Log.d(TAG, "Discovery failed: Error code:" + errorCode);
                NSDMANAGER.stopServiceDiscovery(this);
            }
        };
    }
    @Override
    public void onDestroy() {
        NSDMANAGER.stopServiceDiscovery(DISCOVERYLISTENER);
        NSDMANAGER.unregisterService(REGISTRATIONLISTENER);
        super.onDestroy();
    }

    // FOR POSTING FEEDBACK TASK
    public class beaconTask extends AsyncTask<String,Void,Boolean>
    {
        String json;
        protected void onPreExecute() {
            Map<String, String> comment = new HashMap<String, String>();
            comment.put("UUID", "504C78A4595A4EAFB53BB346EE4549BE");
            comment.put("major", "0014");
            comment.put("minor", "0005");

            json = new GsonBuilder().create().toJson(comment, Map.class);
        }
        protected Boolean doInBackground(String... params) {
            HttpURLConnection urlConnection = null;
            int statusCode = 0;
            try {
                URL urlToRequest = new URL(params[0]);
                urlConnection = (HttpURLConnection) urlToRequest.openConnection();
                //urlConnection.setRequestProperty(LoginActivity.SKYLER_HEADER, LoginActivity.TOKEN);
                urlConnection.setDoOutput(true);
                urlConnection.setRequestMethod("POST");
                urlConnection.setRequestProperty("Content-Type", "application/json");
                urlConnection.connect();

                OutputStream os = urlConnection.getOutputStream();
                BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(os, "UTF-8"));
                writer.write(json);
                writer.close();
                os.close();

                statusCode = urlConnection.getResponseCode();
                Log.d(TAG, "doInBackground: "+ statusCode);

            } catch (MalformedURLException e) {
                Log.d(TAG, " URL ERROR");
            } catch (SocketTimeoutException e) {
                Log.d(TAG, " TIMEOUT ERROR");
            } catch (IOException e) {
                Log.d(TAG, " IO ERROR" + e);
            } finally {
                if (urlConnection != null) {
                    urlConnection.disconnect();
                }
                if (statusCode == HttpURLConnection.HTTP_CREATED) {
                    return true;
                } else {
                    return false;
                }

            }
        }
        protected void onPostExecute(final Boolean success) {
            if (success){
                //if need to perform anything
            }
        }
    }

}
