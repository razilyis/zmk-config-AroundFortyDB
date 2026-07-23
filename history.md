# 開発履歴

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
