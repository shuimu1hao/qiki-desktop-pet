#!/data/data/com.termux/files/usr/bin/bash
# 🐾 琪琪桌宠管理脚本 (=^･ω･^=)
# 用法：
#   bash pet-ctl.sh start   启动桌宠
#   bash pet-ctl.sh stop    关闭桌宠
#   bash pet-ctl.sh restart 重启桌宠
#   bash pet-ctl.sh status  查看运行状态
#
# 日志：~/hermes11/pet/pet-run.log
# 状态：~/hermes11/pet/pet-status.txt（显示在桌宠气泡里）

PET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_DIR=~/hermes11/gui-demo/bin   # termux-am wrapper（绕过 termux-app am.sock 未启用问题）
SKIN="${2:-default}"                   # 皮肤名，可 pet-ctl.sh start 换肤名
RUN_LOG="$PET_DIR/pet-run.log"
STATUS_FILE=~/hermes11/pet-status.txt

is_running() {
  pgrep -f "python3 pet.py" >/dev/null 2>&1
}

cmd_start() {
  if is_running; then
    echo "桌宠已经在跑啦喵～ (pid: $(pgrep -f 'python3 pet.py' | head -1))"
    return 0
  fi
  cd "$PET_DIR" || return 1
  if [ -d "$WRAPPER_DIR" ] && [ -x "$WRAPPER_DIR/termux-am" ]; then
    export PATH="$WRAPPER_DIR:$PATH"
  else
    echo "⚠️ 没找到 $WRAPPER_DIR/termux-am wrapper，termux-gui 可能连不上，建议先创建" >&2
  fi
  nohup python3 pet.py --skin "$SKIN" > "$RUN_LOG" 2>&1 &
  sleep 3
  if is_running; then
    echo "✨ 桌宠启动成功 (pid: $(pgrep -f 'python3 pet.py' | head -1), 皮肤: $SKIN)"
    echo "   关闭用: bash pet-ctl.sh stop"
  else
    echo "❌ 启动失败，看日志: $RUN_LOG" >&2
    tail -5 "$RUN_LOG" >&2
    return 1
  fi
}

cmd_stop() {
  if ! is_running; then
    echo "桌宠本来就没在跑喵～"
    return 0
  fi
  pkill -f "python3 pet.py"
  sleep 1
  if is_running; then
    echo "❌ 没杀掉，手动 kill: $(pgrep -f 'python3 pet.py')" >&2
    return 1
  fi
  rm -f "$STATUS_FILE"   # 顺手清掉状态，下次启动回到待命
  echo "🌙 桌宠已关闭"
}

cmd_restart() {
  cmd_stop
  sleep 1
  cmd_start
}

cmd_status() {
  if is_running; then
    pid="$(pgrep -f 'python3 pet.py' | head -1)"
    echo "🟢 桌宠运行中 (pid: $pid)"
    if [ -f "$STATUS_FILE" ]; then
      echo "   当前状态: $(cat "$STATUS_FILE")"
    fi
  else
    echo "⚪ 桌宠未运行"
  fi
}

case "${1:-}" in
  start)   cmd_start ;;
  stop)    cmd_stop ;;
  restart) cmd_restart ;;
  status)  cmd_status ;;
  *)
    echo "用法: bash pet-ctl.sh {start|stop|restart|status} [皮肤名]"
    echo "示例: bash pet-ctl.sh start         # 默认皮肤 default"
    echo "      bash pet-ctl.sh start 泳装    # 指定皮肤"
    exit 1
    ;;
esac
