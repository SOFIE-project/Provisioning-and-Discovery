package com.example.sofie_dp;

import android.os.Bundle;
import android.os.RemoteException;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import org.altbeacon.beacon.Beacon;
import org.altbeacon.beacon.BeaconConsumer;
import org.altbeacon.beacon.BeaconManager;
import org.altbeacon.beacon.BeaconParser;
import org.altbeacon.beacon.RangeNotifier;
import org.altbeacon.beacon.Region;
import org.altbeacon.beacon.utils.UrlBeaconUrlCompressor;

import java.util.ArrayList;
import java.util.Collection;

public class Eddystone extends AppCompatActivity implements BeaconConsumer, RangeNotifier {
    private static String TAG = "EDDYSTONE";

    private Region region;
    private BeaconManager beaconManager;
    private ArrayAdapter<String> adapter;
    private ArrayList<String> arrayList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_eddystone);
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        ListView list = (ListView) findViewById(R.id.EDDYSTONE);
        arrayList = new ArrayList<>();

        adapter= new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, arrayList);
        list.setAdapter(adapter);

        beaconManager = BeaconManager.getInstanceForApplication(this.getApplicationContext());
        beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout(BeaconParser.EDDYSTONE_URL_LAYOUT));
        beaconManager.bind(this);
        //startScanning();

    }

    @Override
    public void onBeaconServiceConnect() {
        Log.d(TAG, "onConnecting");
        region = new Region("all-beacons", null, null, null);
        try {
            beaconManager.startRangingBeaconsInRegion(region);
        } catch (RemoteException e) {
            Log.e(TAG, e.getMessage());
        }
        beaconManager.addRangeNotifier(this);
    }

    @Override
    public void didRangeBeaconsInRegion(Collection<Beacon> beacons, Region region) {
        Log.d(TAG, "onConnectS");
        for (Beacon beacon: beacons) {
            Log.d(TAG, "onConnect" + beacon.getBluetoothName());

            if (beacon.getServiceUuid() == 0xfeaa && beacon.getBeaconTypeCode() == 0x10) {
                // This is a Eddystone-URL frame
                String url = UrlBeaconUrlCompressor.uncompress(beacon.getId1().toByteArray());
                Log.d(TAG, "I see a beacon transmitting a url: " + url );

                if(beacon.getBluetoothName() != null){
                    if(arrayList.contains(url)){

                    } else if (beacon.getBluetoothName().equals("DPP")){
                        arrayList.add(url);
                        // next thing you have to do is check if your adapter has changed
                        adapter.notifyDataSetChanged();
                    }
                }

            }
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        stopScanning();
    }

    public void stopScanning() {
        if (beaconManager.isBound(this)) {
            try {
                beaconManager.removeAllRangeNotifiers();
                beaconManager.stopRangingBeaconsInRegion(region);
            } catch (RemoteException e) {
                Log.e(TAG, e.getMessage());
            }

            beaconManager.unbind(this);
        }
    }

}