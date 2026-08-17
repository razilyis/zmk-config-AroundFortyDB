# zmk-config-AroundFortyDB

Around Forty DBのファームウェアです。

## 対応構成

- ZMK Firmware v0.4 (Zephyr 4.1 追従)
- board: `xiao_ble//zmk`
- 右手Central: `around_forty_db_right rgbled_adapter`
- 左手Peripheral: `around_forty_db_left rgbled_adapter`
- ZMK Studio（右手USB接続時）

## トラックボール

左右にPMW3610を搭載し、`razilyis/zmk-pmw3610-driver`の
`Dev-v0.4_inertial-scroll`ブランチをWestで取得します。

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

Prospector ScannerはBluetooth接続が不安定になるため、現在は有効化していません。

## ビルド

GitHub Actionsでは`build.yaml`を使用し、右手・左手・設定リセット用ファームウェアを生成します。
