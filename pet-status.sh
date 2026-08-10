#!/bin/bash
# 更新琪琪桌宠状态显示：pet-status.sh "正在处理：xxx"
# 不传参数 = 清除状态（回到待命）
STATUS_FILE=~/hermes11/pet-status.txt
if [ -n "$1" ]; then
  echo "$1" > "$STATUS_FILE"
else
  rm -f "$STATUS_FILE"
fi
echo "桌宠状态: ${1:-（已清除，待命中）}"
