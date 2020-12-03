package com.example.sofie_dp;


import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.content.ComponentName;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.os.Bundle;

import android.os.IBinder;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;


public class Ble extends AppCompatActivity  {
    private static final String TAG = "BLE::";

    BluetoothManager btManager;
    BluetoothAdapter btAdapter;
    BluetoothLeScanner btScanner;
    private UartService mService = null;

    private final static int REQUEST_ENABLE_BT = 1;
    private static final int PERMISSION_REQUEST_COARSE_LOCATION = 1;
    private static final int DATA_TYPE_SERVICE_DATA = 0x24;
    private String deviceAddress;
    private Button configration;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ble);

        btManager = (BluetoothManager)getSystemService(Context.BLUETOOTH_SERVICE);
        btAdapter = btManager.getAdapter();
        btScanner = btAdapter.getBluetoothLeScanner();

        Intent bindIntent = new Intent(this, UartService.class);
        startService(bindIntent);
        bindService(bindIntent, mServiceConnection, Context.BIND_AUTO_CREATE);

        configration = findViewById(R.id.config);
        configration.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Uploading Configration", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
                // Upload configration to the BlE device
                mService.writeRXCharacteristic("".getBytes());

            }
        });
        configration.setVisibility(View.GONE);

        if (btAdapter != null && !btAdapter.isEnabled()) {
            Intent enableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableIntent,REQUEST_ENABLE_BT);
        }

        // Make sure we have access coarse location enabled, if not, prompt the user to enable it
        if (this.checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            final AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setTitle("This app needs location access");
            builder.setMessage("Please grant location access so this app can detect BLE");
            builder.setPositiveButton(android.R.string.ok, null);
            builder.setOnDismissListener(new DialogInterface.OnDismissListener() {
                @Override
                public void onDismiss(DialogInterface dialog) {
                    requestPermissions(new String[]{Manifest.permission.ACCESS_COARSE_LOCATION}, PERMISSION_REQUEST_COARSE_LOCATION);
                }
            });
            builder.show();
        }
        // Start BLE scan
        startScanning();
    }

    // Device scan callback.
    private ScanCallback leScanCallback = new ScanCallback() {
        @Override
        public void onScanResult(int callbackType, ScanResult result) {
            if(result.getDevice().getName() != null) {
                byte[] scanRecord = Objects.requireNonNull(result.getScanRecord()).getBytes();
                deviceAddress = result.getDevice().getAddress();
                parseServiceDataFromBytes(scanRecord);
            }
        }
    };

    private void parseServiceDataFromBytes(byte[] scanRecord) {
        int currentPos = 0;
        try {
            while (currentPos < scanRecord.length) {
                int fieldLength = scanRecord[currentPos++] & 0xff;
                if (fieldLength == 0) {
                    break;
                }
                int fieldType = scanRecord[currentPos] & 0xff;
                if (fieldType == DATA_TYPE_SERVICE_DATA) {
                    // Stop BLE scan
                    stopScanning();
                    Map<Integer,String> ret;
                    ret = ParseRecord(scanRecord);
                    String URL =hexToASCII(Objects.requireNonNull(ret.get(DATA_TYPE_SERVICE_DATA)));
                    mService.initialize();
                    if(mService.connect(deviceAddress)){
                        configration.setVisibility(View.VISIBLE);
                        new downloadSemantic();
                    }

                    return;
                }
                currentPos += fieldLength;
            }
        } catch (Exception e) {
            Log.e(TAG, "Unable to parse scan record: " + Arrays.toString(scanRecord), e);
        }
    }

    private static String hexToASCII(String hexValue)
    {
        StringBuilder output = new StringBuilder();
        for (int i = 0; i < hexValue.length(); i += 2)
        {
            String str = hexValue.substring(i, i + 2);
            output.append((char) Integer.parseInt(str, 16));
        }
        return output.toString();
    }

    static public  Map <Integer,String>  ParseRecord(byte[] scanRecord){
        Map<Integer,String> ret = new HashMap<>();
        int index = 0;
        while (index < scanRecord.length) {
            int length = scanRecord[index++];
            if (length == 0) break;
            int type = scanRecord[index];
            if (type == 0) break;
            byte[] data = Arrays.copyOfRange(scanRecord, index + 1, index + length);
            if(data != null && data.length > 0) {
                StringBuilder hex = new StringBuilder(data.length * 2);
                for (int bb = 0; bb <= data.length- 1; bb++){
                    hex.append(String.format("%02X", data[bb]));
                }
                ret.put(type,hex.toString());
            }
            index += length;
        }
        return ret;
    }

    private ServiceConnection mServiceConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName className, IBinder rawBinder) {
            Log.d(TAG, "onServiceConnected: I AM HERE");
            mService = ((UartService.LocalBinder) rawBinder).getService();
        }

        @Override
        public void onServiceDisconnected(ComponentName classname) {
            mService.disconnect();
            mService = null;
        }
    };

    @Override
    public void onPause() {
        super.onPause();
        stopScanning();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        switch (requestCode) {
            case PERMISSION_REQUEST_COARSE_LOCATION: {
                if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    System.out.println("Coarse location permission granted");
                } else {
                    final AlertDialog.Builder builder = new AlertDialog.Builder(this);
                    builder.setTitle("Functionality limited");
                    builder.setMessage("Since location access has not been granted, this app will not be able to discover beacons when in the background.");
                    builder.setPositiveButton(android.R.string.ok, null);
                    builder.setOnDismissListener(new DialogInterface.OnDismissListener() {

                        @Override
                        public void onDismiss(DialogInterface dialog) {
                        }

                    });
                    builder.show();
                }
            }
        }
    }

    public static class downloadSemantic extends AsyncTask<String,Void,Boolean>
    {
        String json;
        protected void onPreExecute() {

        }
        protected Boolean doInBackground(String... params) {
            HttpURLConnection urlConnection = null;
            int statusCode = 0;
            try {
                URL urlToRequest = new URL(params[0]);
                urlConnection = (HttpURLConnection) urlToRequest.openConnection();
                urlConnection.setDoOutput(true);
                urlConnection.setRequestMethod("GET");
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
        }
    }

    public void startScanning() {
        System.out.println("start scanning");
        AsyncTask.execute(new Runnable() {
            @Override
            public void run() {
                btScanner.startScan(leScanCallback);
            }
        });
    }

    public void stopScanning() {
        System.out.println("stopping scanning");
        AsyncTask.execute(new Runnable() {
            @Override
            public void run() {
                btScanner.stopScan(leScanCallback);
            }
        });
    }
}
