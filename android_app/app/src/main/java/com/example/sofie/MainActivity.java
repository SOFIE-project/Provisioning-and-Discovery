package com.example.sofie;

import android.app.Activity;
import android.app.Service;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.IBinder;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.view.ViewGroup;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
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
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class MainActivity extends AppCompatActivity {
    private Intent NSD_SERVICE;
    public static ArrayAdapter adapter;
    public static ArrayList<NsdServiceInfo> NSD_DEVICES;

    private static final String TAG = "NSD::";

    public NsdManager NSDMANAGER;
    public NsdManager.RegistrationListener REGISTRATIONLISTENER;
    public NsdManager.DiscoveryListener DISCOVERYLISTENER;

    public String SERVICENAME;
    public int LOCALPORT;
    public String ID;

    public ServerSocket SERVERSOCKET;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);


        FloatingActionButton fab = findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });



        NSD_DEVICES  = new ArrayList<NsdServiceInfo>();

        NSDMANAGER = (NsdManager) getApplicationContext().getSystemService(Context.NSD_SERVICE);

        initializeDiscoveryListener();
        //initializeRegistrationListener();
        initializeServerSocket();
        this.discoverServices();

        //this.registerService(LOCALPORT);
        adapter = new discoveryAdapter(this, R.layout.row_item, NSD_DEVICES);
        ListView listView = (ListView) findViewById(R.id.mobile_list);
        listView.setAdapter(adapter);

        Toast.makeText(this, "NSD Started",Toast.LENGTH_SHORT).show();


        //NSD_SERVICE = new Intent(this, NSD.class);
        //startService(NSD_SERVICE);



    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
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

                                if (serviceInfo.getServiceName().equals(SERVICENAME)) {
                                    Log.d(TAG, "Same IP.");
                                    return;
                                }
                                if (!NSD_DEVICES.contains(serviceInfo)){
                                    NSD_DEVICES.add(serviceInfo);
                                    //adapter.add(serviceInfo);
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
            NSDMANAGER.stopServiceDiscovery(DISCOVERYLISTENER);
            NSDMANAGER.unregisterService(REGISTRATIONLISTENER);
            super.onDestroy();
        }

        public class discoveryAdapter extends ArrayAdapter<NsdServiceInfo> {
            private Context mContext;
            NsdServiceInfo user;

            public discoveryAdapter(Context context, int resourses, ArrayList<NsdServiceInfo> objects) {
                super(context, resourses, objects);
                mContext = context;
            }


            @Override
            public View getView(int position, View convertView, ViewGroup parent) {
                //View v=((Activity)getContext()).getLayoutInflater().inflate(R.layout.row_item,null);
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
                Name.setText(user.getServiceName());
                host.setText(user.getHost().toString() + ":" + user.getPort());
                type.setText(user.getServiceType());

                textfields.setText(new String(user.getAttributes().get("url")));

                // Return the completed view to render on screen

                Name.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        new AlertDialog.Builder(getContext())
                                .setTitle("Provision Device")
                                .setMessage("Are you sure you want to provision the device")
                                .setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface dialog, int which) {
                                        String URL = "http://" + user.getHost().getHostAddress()+ ":5000/api/iBeacon";
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

                return convertView;

            }
        }

        // FOR POSTING FEEDBACK TASK
        public class beaconTask extends AsyncTask<String,Void,Boolean>
        {
            String json;
            protected void onPreExecute() {
                Map<String, String> comment = new HashMap<String, String>();
                comment.put("UUID", "504C78A4595A4EAFB53BB346EE4549BE");
                comment.put("major", "0014");
                comment.put("minor", "0001");

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
