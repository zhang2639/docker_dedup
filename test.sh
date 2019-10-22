#!/bin/bash

for Filename in `ls /home/zhangshiqiang/docker_test/overlay2`

do
  if [ $Filename = "l" ]
  then
    continue
  fi

  python api.py add /home/zhangshiqiang/docker_test/overlay2/$Filename/diff

done
