# zmk-config-AroundFortyDB

Around Forty DBのファームウェアです。

## 対応構成

- ZMK Firmware v0.3.0
- board: `seeeduino_xiao_ble`
- 右手Central: `around_forty_db_right rgbled_adapter`
- 左手Peripheral: `around_forty_db_left rgbled_adapter`
- ZMK Studio（右手USB接続時）

## トラックボール

左右にPMW3610を搭載し、`razilyis/zmk-pmw3610-driver`の
`Dev-v0.3_inertial-scroll`ブランチをWestで取得します。

- 左右スクロールの慣性スクロール
- 慣性スクロールのON/OFF
- 縦・横スクロール方向の反転
- 右手の低速カーソル安定化
- 入力集中時のキー取りこぼし・連続入力を抑えるキュー調整
- 右手のスクロールレイヤー6・7で慣性を有効化
- 左手のスクロールは全レイヤーで慣性を有効化

## その他

- Windows / macOS用のキーマップ
- 全角・半角切り替えマクロ
- Slow Cursorレイヤー
- 2種類のScrollレイヤー
- ZMK Studio対応
- Adafruit nRF52 BootloaderのBluetooth OTA DFU modeへ移行する`&ble_dfu` behavior

## BLE DFU PoC

`razilyis/zmk-feature-ble-dfu`をWestで取得し、左右shieldで`CONFIG_ZMK_BLE_DFU=y`を有効にしています。Settings layerへ`&ble_dfu_ota` wrapper macroを配置しています。

`&ble_dfu_ota`を押すと、現在は確認画面なしでAdafruit nRF52 BootloaderのOTA modeへ再起動します。USB UF2で復旧できる状態を確認してから使用してください。FirmwareのBluetooth転送はまだ実装していません。

Keymap Editorでは外部moduleの独自behaviorを直接認識できないため、keymap内の標準macro wrapper `&ble_dfu_ota`をbehavior pickerから選択します。

Prospector ScannerはBluetooth接続が不安定になるため、現在は有効化していません。

## ビルド

GitHub Actionsでは`build.yaml`を使用し、右手・左手・設定リセット用ファームウェアを生成します。
