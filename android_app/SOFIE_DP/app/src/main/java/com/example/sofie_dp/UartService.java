package com.example.sofie_dp;

import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.content.Context;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;

import java.util.UUID;

import static android.bluetooth.BluetoothProfile.STATE_CONNECTED;

public class UartService extends Service {
    private final static String TAG = "UART::";

    private BluetoothManager btManager;
    private BluetoothAdapter btAdapter;
    private String btDeviceAddress;
    private BluetoothGatt btGatt;

    public static final UUID RX_SERVICE_UUID = UUID.fromString("6e400001-b5a3-f393-e0a9-e50e24dcca9e");
    public static final UUID RX_CHAR_UUID = UUID.fromString("6e400002-b5a3-f393-e0a9-e50e24dcca9e");

    private final BluetoothGattCallback mGattCallback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            if (newState == STATE_CONNECTED) {
                Log.d(TAG, "Connected to GATT server.");
                // Attempts to discover services after successful connection.
                Log.d(TAG, "Attempting to start service discovery:" + btGatt.discoverServices());
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.d(TAG, "Disconnected from GATT server.");
            }
        }

        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                Log.d(TAG, "mBluetoothGatt = " + btGatt.getServices());
            } else {
                Log.d(TAG, "onServicesDiscovered received: " + status);
            }
        }

    };

    public boolean initialize() {
        if (btManager == null) {
            btManager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
            if (btManager == null) {
                Log.d(TAG, "Unable to initialize BluetoothManager.");
                return false;
            }
        }
        btAdapter = btManager.getAdapter();
        if (btAdapter == null) {
            Log.e(TAG, "Unable to obtain a BluetoothAdapter.");
            return false;
        }
        return true;
    }

    public class LocalBinder extends Binder {
        UartService getService() {
            return UartService.this;
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    @Override
    public boolean onUnbind(Intent intent) {
        return super.onUnbind(intent);
    }

    private final IBinder mBinder = new LocalBinder();

    public boolean connect(final String address) {
        if (btAdapter == null || address == null) {
            Log.d(TAG, "BluetoothAdapter not initialized or unspecified address.");
            return false;
        }

        // Previously connected device.  Try to reconnect.
        if (btDeviceAddress != null && address.equals(btDeviceAddress) && btGatt != null) {
            Log.d(TAG, "Trying to use an existing mBluetoothGatt for connection.");
            if (btGatt.connect()) {
                return true;
            } else {
                return false;
            }
        }

        final BluetoothDevice device = btAdapter.getRemoteDevice(address);
        if (device == null) {
            Log.w(TAG, "Device not found.  Unable to connect.");
            return false;
        }
        // We want to directly connect to the device, so we are setting the autoConnect
        // parameter to false.
        btGatt = device.connectGatt(this, false, mGattCallback);
        Log.d(TAG, "Trying to create a new connection.");
        btDeviceAddress = address;
        return true;
    }

    public void writeRXCharacteristic(byte[] value)
    {
        BluetoothGattService RxService = btGatt.getService(RX_SERVICE_UUID);
        Log.d(TAG,"btGatt null"+ btGatt.getService(RX_CHAR_UUID));
        if (RxService == null) {
            Log.d(TAG,"Rx service not found!");
            //return;
        }
        BluetoothGattCharacteristic RxChar = RxService.getCharacteristic(RX_CHAR_UUID);
        if (RxChar == null) {
            Log.d(TAG,"Rx charateristic not found!");
            return;
        }
        RxChar.setValue(value);
        boolean status = btGatt.writeCharacteristic(RxChar);

        Log.d(TAG, "write TXchar - status=" + status);
    }

    public void disconnect() {
        if (btAdapter == null || btGatt == null) {
            Log.d(TAG, "BluetoothAdapter not initialized");
            return;
        }
        btDeviceAddress = null;
        btGatt.disconnect();
        btGatt.close();
    }

}
