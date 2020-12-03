package com.example.sofie_dp;

import android.content.Context;
import android.content.DialogInterface;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.gson.GsonBuilder;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ServerSocket;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;


public class Dns extends AppCompatActivity {

    private static final String TAG = "NSD::";

    public static ArrayAdapter adapter;
    public static ArrayList<NsdServiceInfo> NSD_DEVICES;
    public NsdManager NSDMANAGER;
    public NsdManager.DiscoveryListener DISCOVERER;

    public String SERVICENAME;
    public int LOCALPORT;
    private static final String SERVICETYPE = "_webthing._tcp.";
    public ServerSocket SERVERSOCKET;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dns);
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);


        NSD_DEVICES  = new ArrayList<>();
        NSDMANAGER = (NsdManager) getApplicationContext().getSystemService(Context.NSD_SERVICE);
        initializeDiscoveryListener();
        initializeServerSocket();
        this.discoverServices();
        adapter = new discoveryAdapter(this, R.layout.row_item, NSD_DEVICES);
        ListView listView = (ListView) findViewById(R.id.mobile);
        listView.setAdapter(adapter);

        Toast.makeText(this, "NSD Started",Toast.LENGTH_SHORT).show();
    }

    public void discoverServices() {
        NSDMANAGER.discoverServices(SERVICETYPE, NsdManager.PROTOCOL_DNS_SD, DISCOVERER);
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
        DISCOVERER = new NsdManager.DiscoveryListener() {
            @Override
            public void onDiscoveryStarted(String regType) {
                Log.d(TAG, "Service discovery started");
            }

            @Override
            public void onServiceFound(NsdServiceInfo service) {
                SERVICENAME = service.getServiceName();
                if (!service.getServiceType().equals(SERVICETYPE)) {
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

                            if (serviceInfo.getServiceName().equals(SERVICENAME)) {
                                Log.d(TAG, "Same IP.");
                                return;
                            }
                            if (!NSD_DEVICES.contains(serviceInfo)){
                                NSD_DEVICES.add(serviceInfo);
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        adapter.notifyDataSetChanged();
                                    }
                                });
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
        NSDMANAGER.stopServiceDiscovery(DISCOVERER);
        super.onDestroy();
    }

    public static class discoveryAdapter extends ArrayAdapter<NsdServiceInfo> {
        NsdServiceInfo user;

        public discoveryAdapter(Context context, int resourses, ArrayList<NsdServiceInfo> objects) {
            super(context, resourses, objects);
        }
        

        @Override
        public View getView(final int position, View convertView, ViewGroup parent) {
            user = getItem(position);
            // Check if an existing view is being reused, otherwise inflate the view
            if (convertView == null) {
                convertView = LayoutInflater.from(getContext()).inflate(R.layout.row_item, parent, false);
            }
            // Lookup view for data population
            TextView Name = (TextView) convertView.findViewById(R.id.deviceName);
            TextView host = (TextView) convertView.findViewById(R.id.host);
            TextView type = (TextView) convertView.findViewById(R.id.type);
            TextView textfields = (TextView) convertView.findViewById(R.id.content);

            // Populate the data into the template view using the data object
            Name.setText(Objects.requireNonNull(getItem(position)).getServiceName());
            host.setText(Objects.requireNonNull(getItem(position)).getHost().toString() + ":" + user.getPort());
            type.setText(Objects.requireNonNull(getItem(position)).getServiceType());

            if(Objects.requireNonNull(getItem(position)).getAttributes().containsKey("url")){
                textfields.setText(new String(Objects.requireNonNull(getItem(position)).getAttributes().get("url")));
                Name.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        new AlertDialog.Builder(getContext())
                                .setTitle("Provision Device")
                                .setMessage("Are you sure you want to provision the device: " + Objects.requireNonNull(getItem(position)).getServiceName())
                                .setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface dialog, int which) {
                                        String URL = "http://" + Objects.requireNonNull(getItem(position)).getHost().getHostAddress()+ ":5000/api/iBeacon";
                                        beaconTask beacon = new beaconTask();
                                        beacon.execute(URL);
                                    }
                                })

                                // A null listener allows the button to dismiss the dialog and take no further action.
                                .setNegativeButton(android.R.string.no, null)
                                .setIcon(android.R.drawable.ic_dialog_alert)
                                .show();
                    }
                });
            } else{
                
                Name.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        new AlertDialog.Builder(getContext())
                                .setTitle("Error")
                                .setMessage("You cannot provision this device: " + Objects.requireNonNull(getItem(position)).getServiceName())
                                .setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface dialog, int which) {
                                    }
                                })
                                .setIcon(android.R.drawable.ic_dialog_alert)
                                .show();
                    }
                });
            }

            return convertView;

        }
    }

    public static class beaconTask extends AsyncTask<String,Void,Boolean>
    {
        String json;
        protected void onPreExecute() {
            Map<String, String> comment = new HashMap<>();
            json = new GsonBuilder().create().toJson(comment, Map.class);
        }
        protected Boolean doInBackground(String... params) {
            HttpURLConnection urlConnection = null;
            int statusCode = 0;
            try {
                URL urlToRequest = new URL(params[0]);
                urlConnection = (HttpURLConnection) urlToRequest.openConnection();
                urlConnection.setDoOutput(true);
                urlConnection.setRequestMethod("POST");
                urlConnection.setRequestProperty("Content-Type", "application/json");
                urlConnection.connect();

                OutputStream os = urlConnection.getOutputStream();
                BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(os, StandardCharsets.UTF_8));
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
            }
            return statusCode == HttpURLConnection.HTTP_CREATED;
        }
        protected void onPostExecute(final Boolean success) {
            //if need to perform anything
        }
    }

}
