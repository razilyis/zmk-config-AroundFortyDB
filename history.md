# 開発履歴

## 2026-08-04

### Adafruit Legacy DFU package生成を追加

- 成功済みFirmware Artifactの左右UF2がfamily ID `0xADA52840`、application start `0x27000`であることを確認した。
- UF2のtarget addressを保持したIntel HEXへ変換する`scripts/uf2_to_ihex.py`を追加した。family ID、block順序、重複data、application start、flash範囲を検証し、不正な入力を拒否する。
- GitHub Actionsへ`package-ble-dfu` jobを追加し、公式`adafruit-nrfutil 0.5.3.post16`から左右別のNordic Legacy DFU ZIPを生成するようにした。device typeは`0x0052`、SoftDevice requirementは互換値`0xFFFE`、application versionはActions run numberを使用する。
- `firmware-ble-dfu` Artifactへ左右DFU ZIP、従来のUSB復旧用UF2、repository／branch／run／commit／side／SHA-256／sizeを含む`firmware-manifest.json`を格納するようにした。既存`firmware` Artifactは変更していない。

確認結果:

- run `30883794498`の実Artifactから左191,488 byte、右274,944 byteのapplication imageを復元した。
- 固定版`adafruit-nrfutil`で左192,373 byte、右275,835 byteのDFU ZIPをローカル生成した。各ZIPにapplication BIN、14 byteのinit packet DAT、DFU version 0.5の`manifest.json`が含まれ、device type `82`、SoftDevice requirement `65534`、CRC16が設定されることを確認した。
- 初回Actions run `30885876479`は全jobが成功し、`firmware-ble-dfu` Artifactの左右ZIP、init packet、manifestのsize／SHA-256一致を確認した。中間Intel HEXもArtifactへ含まれていたため、最終Artifactには含めないよう出力directoryを分離した。
- 最終Actions run `30886171430`も全jobが成功した。`firmware-ble-dfu` Artifactは左右DFU ZIP、左右／settings resetのUSB復旧用UF2、`firmware-manifest.json`の6fileだけとなり、左右ZIPのsize／SHA-256一致を再確認した。
- Bluetooth経由の実機転送は未確認である。

### BLE DFU Bootloader移行PoCを導入

- `zmk-feature-ble-dfu`をWest moduleへ追加し、左右shieldで`CONFIG_ZMK_BLE_DFU=y`を有効化した。
- `around_forty_db.keymap`で`<behaviors/ble_dfu.dtsi>`を読み込み、Adafruit nRF52 BootloaderのOTA reset type `0xA8`を発行する`&ble_dfu`を利用可能にした。
- Keymap Editorのbehavior pickerから選択できるよう、標準`zmk,behavior-macro`の`&ble_dfu_ota` wrapperをkeymap内へ追加した。
- Settings layerへ`&ble_dfu_ota`を1キー割り当てた。現状は押下直後に再起動し、Firmware転送や確認操作は未実装である。

確認結果:

- 初回GitHub Actions run `30883503833`はmoduleのCMake include path不足により左右buildが失敗した。module側へ`zephyr_include_directories(include)`を追加した。
- 修正後run `30883794498`で右central、左peripheral、settings reset、artifact mergeの全jobが成功した。
- ユーザーがKeymap Editorで`&ble_dfu_ota`がCustom macro「BLE_DFU_OTA」として表示されることを実画面確認した。
- 右central／左peripheralへFirmwareを書き込み、`&ble_dfu_ota`押下で通常接続が切断されることを確認した。WindowsのBLE scanで`AdaDFU`とNordic Legacy DFU service UUID `00001530-1212-efde-1523-785feabcd123`を検出し、reset 1回で通常Firmwareへ復帰した。DFU package転送は未確認である。

## 2026-07-31

### dev-main PMW3610 SPI・蓄積デルタ対策版への更新

- **目的**: 左右PMW3610のSPI設定失敗と、異常値・微小入力後に古い移動量が遅れて出力される可能性を抑える。
- **変更内容**:
  - `config/west.yml`の`zmk-pmw3610-driver`をコミット`e3d60ed54b928dff07fbdc9dbf67cf40f35d33b6`へ更新。
  - PMW3610のCS保持時間と書き込み間隔を確保し、異常サンプル時の蓄積デルタ破棄を取り込む。
- **影響範囲**:
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right` / `around_forty_db_left`
  - split: 右Central / 左Peripheral。
  - レイヤー、キー配置、CPI、XY変換、スクロール感度、SPI/IRQ配線、BLE設定は変更なし。

### dev-main PMW3610暴走対策版の再ビルド

- **目的**: `Dev-v0.3_inertial-scroll`の最新暴走対策をDBのGitHub Actionsビルドへ反映する。
- **変更内容**:
  - `config/west.yml`の`zmk-pmw3610-driver`をコミット`c74b37c526547fa7931c9e855362176599fdeae1`へ更新。
- **影響範囲**:
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right` / `around_forty_db_left`
  - split: 右Central / 左Peripheral。
  - レイヤー、キー配置、CPI、XY変換、SPI/IRQ配線、BLE設定は変更なし。

### dev-main PMW3610微小振動フィルタの有効化

- **目的**: 打鍵・クリック時の微小振動をPMW3610のカーソル・スクロール入力として扱わないようにする。
- **変更内容**:
  - 左右PMW3610の`motion-threshold`を`0`から`1`へ変更。
  - X/Yの絶対値が両方とも1以下のサンプルを破棄。
- **影響範囲**:
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right` / `around_forty_db_left`
  - split: 右Central / 左Peripheral。
  - 左右トラックボールを使用する全レイヤー。
  - CPI、XY変換、キー配置、SPI/IRQ、BLE設定は変更なし。

### dev-main PMW3610安全性修正版の固定

- **目的**: `dev-main`のGitHub Actionsで、慣性スクロール機能を維持しながら入力輻輳・未完フレーム・IRQ異常への安全性修正を再現可能にする。
- **変更内容**:
  - `config/west.yml`の`zmk-pmw3610-driver`を、`Dev-v0.3_inertial-scroll`で検証したコミット`fe219c7eb267050fff6743f00b51c7cf6b029839`へ固定。
  - PMW3610処理の専用work queue化、入力再送の時間・移動量制限、未完X/Yフレームの回復、IRQ再確認を適用。
- **影響範囲**:
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right` / `around_forty_db_left`
  - split: 右Central / 左Peripheral。
  - 右は通常カーソルとレイヤー6・7の慣性スクロール、左はスクロール動作。
  - `motion-threshold`、CPI、XY変換、キー配置、SPI/IRQ配線、BLE接続数は変更なし。
  - 専用work queueにより片側約1.8KBのRAMを追加使用。

## 2026-07-24

### 左右トラックボールの微操作改善

- **目的**: 左右PMW3610で低速・微小移動が欠落し、右カーソルと左スクロールの細かな操作が段階的になる症状を改善する。
- **ブランチ**: `dev-main`
- **変更内容**:
  - `around_forty_db_right.overlay`: `motion-threshold` を `1` から `0` に変更し、±1カウントの移動を破棄しない。
  - `around_forty_db_right.conf`: `CONFIG_PMW3610_REPORT_INTERVAL_MIN` を `10ms` から `5ms` に短縮。
  - `around_forty_db_left.overlay`: `motion-threshold` を `1` から `0` に変更し、細かなスクロール入力を破棄しない。
  - `around_forty_db_left.conf`: `CONFIG_PMW3610_REPORT_INTERVAL_MIN` を `15ms` から `5ms` に短縮。
- **影響範囲**:
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right` / `around_forty_db_left`
  - split: 右Central / 左Peripheral。
  - レイヤー: 左右トラックボールを使う全レイヤー。
  - CPI、XY変換、スクロール変換、BLE設定、input listener構成は変更なし。

### GitHub Actions向けPMW3610依存の固定

- **目的**: ローカルパスに依存せず、GitHub ActionsのWest初期化で今回検証したPMW3610ドライバーを再現可能にする。
- **変更内容**:
  - `config/west.yml` の `zmk-pmw3610-driver` を、GitHubへ公開済みのコミット `8b605942880d46e3e2ab5b510fc47dd47f052440` に固定。
  - 参照先は `https://github.com/razilyis/zmk-pmw3610-driver`。
- **CI構成**:
  - workflow: `.github/workflows/build.yml`
  - reusable workflow: `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3.0`
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right rgbled_adapter` / `around_forty_db_left rgbled_adapter`
  - West依存取得はreusable workflow内で実行。
  - `zmk-module-runtime-input-processor` は、ZMK v0.3互換かつローカル検証済みの `8103d0618856a099369f86e93b462ee987cf159a` に固定。
  - その他のcormoranモジュールもローカル検証済みコミットに固定し、`main`更新によるZMK v0.3 API不整合を防止。

### ZMK Keymap EditorへのBehavior公開

- **目的**: Westモジュール内の定義を直接読まないKeymap Editorでも、カスタムBehaviorを選択可能にする。
- **変更内容**:
  - `PMW3610 Inertia Toggle` をkeymap内に定義し、慣性スクロールON/OFF Behaviorを公開。
  - 既存のセンサー回転Behaviorに `SCROLL_UP_DOWN` ラベルを追加し、スクロール方向Behaviorを公開。
- **影響範囲**:
  - `config/around_forty_db.keymap` のBehaviorメタデータのみ。
  - 既存のキー配置および実行時動作は変更なし。

### 縦スクロール方向トグルと高解像度スクロール

- **目的**: 縦スクロールの正転・逆転をキーで切り替え、対応するmacOS / Windowsホストで慣性スクロールをより滑らかにする。
- **変更内容**:
  - `PMW3610 Vertical Scroll Direction Toggle` をKeymap Editorへ公開。
  - 右Centralで `CONFIG_ZMK_POINTING_SMOOTH_SCROLLING=y` を有効化し、対応ホストが設定するHID Resolution Multiplierを使用。
  - `config/west.yml` のPMW3610依存を、方向トグル実装済みの `59971c289f3d512fb19b37dd22b58569c84009bb` に更新。
- **影響範囲**:
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right` / `around_forty_db_left`
  - split: BehaviorはGlobalとして右Centralと左Peripheralの両方へ配送。
  - レイヤー: 左は全スクロール入力、右は `inertial-scroll-layers = <6 7>` のみ方向反転。
  - 既存のCPI、XY変換、慣性ゲイン・減衰・周期は変更なし。

### 高解像度スクロール向け慣性ゲイン調整

- **目的**: 高解像度HIDスクロール有効化後に弱く感じる慣性移動量を補う。
- **変更内容**:
  - 左右の `inertial-scroll-gain-pct` を `130` から `250` に変更。
  - 減衰率 `99%`、更新周期 `10ms`、停止閾値 `4` は維持。
- **影響範囲**:
  - 左手Peripheralのスクロール全般。
  - 右手Centralのスクロールレイヤー6・7。
  - 通常カーソル、CPI、XY変換、BLE設定は変更なし。

### タッチパッド型の慣性速度推定

- **目的**: 最後のセンサーレポートだけで慣性初速が決まる挙動を改善し、Macのタッチパッドに近いフリック感へ調整。
- **変更内容**:
  - `zmk-pmw3610-driver` を `fed9a3fc343ad1e18d28de7511331318da1308f5` に更新。
  - 直近のジェスチャー速度を平滑化し、加速には速く、減速には緩やかに追従。
  - 80msを超える入力間隔または方向反転で速度履歴をリセット。
- **影響範囲**:
  - 左手Peripheralのスクロール全般。
  - 右手Centralのスクロールレイヤー6・7。
  - 通常カーソル、CPI、XY変換、BLE設定は変更なし。
  - 片側あたりRAM約16バイト、Flash約208バイト増加。

### 左手スクロール方向トグルの軸補正

- **目的**: 右手では機能する縦スクロール方向トグルが、90度異なる向きで搭載した左手センサーでは機能しない問題を修正。
- **変更内容**:
  - `zmk-pmw3610-driver` を `0c299e78405038ca66c2bf09f048b2bd7dcbc913` に更新。
  - 左手PMW3610へ `vertical-scroll-uses-x-axis` を指定。
  - 左手では生のX軸を反転してから通常スクロールと慣性速度を生成。
- **影響範囲**:
  - 左手Peripheralの縦スクロールと慣性スクロール。
  - 右手Centralは従来どおり生のY軸を反転。
  - CPI、BLEおよびメモリー設定は変更なし。

### dev-main-v2 PMW3610安全性・縦横スクロール更新

- **目的**: 既存`dev-main`を保全し、PMW3610 v2で暴走・フリーズ耐性、片側センサー互換性、縦横スクロール制御を検証。
- **変更内容**:
  - `dev-main-v2`を`dev-main`から分岐。
  - `zmk-pmw3610-driver`をv2コミット`c6fcc9d9318cdd8dc0736faa42ce1d643cefb090`へ固定。
  - Keymap Editor向けに`PMW3610 Horizontal Scroll Direction Toggle`を追加。
  - 慣性ON/OFF、縦方向反転、横方向反転をGlobal Behaviorとして左右へ配送。
  - 慣性更新を100Hz（10ms）から125Hz（8ms）へ変更し、減衰率を99.20%へ高精度化。
- **左右構成**:
  - 左手Peripheralは全レイヤーのスクロールで慣性を使用。
  - 右手Centralはスクロールレイヤー6・7で慣性を使用。
  - 左手は生X軸を縦、右手は生Y軸を縦として方向反転。
- **影響範囲**:
  - 通常スクロールと慣性スクロール。
  - BLE設定、CPI、XY変換、通常キー入力は変更なし。

### dev-main-v2 低速カーソル安定化

- **目的**: 右手トラックボールをゆっくり動かした際の±1カウント由来のカーソルぶれを軽減。
- **変更内容**:
  - 右手PMW3610で低速マイクロモーション安定化を有効化。
  - 閾値1カウント、方向履歴タイムアウト30msに設定。
  - 単発の逆方向入力を保留・相殺し、同方向入力と継続する方向転換は距離を保持して出力。
- **影響範囲**:
  - 右手Centralの通常カーソルとスローカーソル。
  - スクロールレイヤー6・7、左手スクロール、慣性スクロールは処理をバイパス。
  - CPI、BLE、XY変換、通常キー入力は変更なし。

### dev-main-v2 右手スクロール感度・慣性微調整

- **目的**: 右手スクロールを少し穏やかにし、慣性の終わり方をより長く滑らかにする。
- **変更内容**:
  - スクロールレイヤー6・7の倍率を`7/8`から`4/5`へ変更し、感度を約8.6%低減。
  - 125Hz（8ms）の更新周期を維持。
  - tickごとの速度保持率を99.20%から99.30%へ変更し、減衰時間を約14%延長。
- **Behavior確認**:
  - 慣性ON/OFFは`BEHAVIOR_LOCALITY_GLOBAL`でCentralと接続中のPeripheralへ配送。
  - 左手切断中の切替は左手へ届かないため、再接続時に左右の状態がずれる可能性がある。
- **影響範囲**:
  - 右手Centralのスクロールレイヤー6・7と右手慣性スクロール。
  - 左手スクロール、カーソル、CPI、BLE、通常キー入力は変更なし。

## 2026-07-25

### dev-mainへのdev-main-v2統合準備

- **目的**: 実機検証済みの`dev-main-v2`を正規の`dev-main`へ統合し、PMW3610依存を正規ブランチ名へ一本化する。
- **変更内容**:
  - `config/west.yml`のPMW3610参照を`Dev-v0.3_inertial-scroll`へ変更。
  - READMEを左右PMW3610、慣性スクロール、縦横方向トグル、低速安定化、入力キュー調整の現行構成に更新。
- **CI構成**:
  - workflow: `.github/workflows/build.yml`
  - reusable workflow: `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3.0`
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right rgbled_adapter` / `around_forty_db_left rgbled_adapter` / `settings_reset`
  - West依存取得はreusable workflow内で実行。
- **確認内容**:
  - West 1.5.0でマニフェストを検証し、68プロジェクトを解決。
  - 左右ファームウェアをクリーン再ビルド。
  - 左手: FLASH 23.90%、RAM 26.00%。
  - 右手: FLASH 37.18%、RAM 43.82%。
- **影響範囲**:
  - 右手Centralと左手Peripheralのビルド依存。
  - レイヤー、キー配置、BLE、メモリー設定、センサー配線は変更なし。
