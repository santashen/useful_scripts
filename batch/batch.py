# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: lab
#     language: python
#     name: lab
# ---

# +
import os
import re
import shutil

import numpy as np
from hpc import Hpc


# -

class Batch(Hpc):
    """在Hpc类的基础上，针对多力场、多工况的分子模拟计算in文件的批量修改上传与结果管理.
    
    执行逻辑：
        将统一的in文件、参数文件、data文件等写好放置在template_folder中，
        针对不同的力场、温度、压力等，每一工况分别建立文件夹，按照树状结构储存在batch_folder文件夹中，
        在服务器上也有相同结构的子文件夹，放置在server_folder文件夹中，
        采用change_input_file函数对每一工况的in文件进行修改，具体修改形式视处理的问题而定，
        通过bsub_work函数实现in文件的提交.
        
    Examples：
        with Batch() as batch:
            for temperature in np.arange(300, 700, 50):
                for pressure in [30]:
                current_folder, relative_path = batch.create_sub_folder(temperature, pressure)
                batch.copy_template(current_folder)
                batch.change_input_file(current_folder, pressure, temperature)
                server_sub_folder = os.path.join(batch.server_folder, relative_path).replace('\\','/')
                batch.upload(current_folder, server_sub_folder)
                batch.bsub_work(server_sub_folder,4,24)
    
    Attributes:
        name: 采用太湖之光服务器(探索100欠费了)
        force_field: 采用的力场
        template_folder: 储存统一的in文件、data文件等，每一个工况都对应一个与该文件夹相同的文件结构.
        batch_folder: 储存不同工况的父级目录
        server_folder: 服务器上储存不同工况的父级目录
        in_file: lammps的in文件名称
    """

    def __init__(
        self,
        name="sunway",
        force_field="Trappe",
        template_folder="E:\\DeskTop\\杂物\\分子模拟\\Trappe写入文件",
        batch_folder="E:\\DeskTop\\杂物\\分子模拟",
        server_folder="/GFPS8p/caoby/shen/MD",
        in_file="in.npt",
    ):
        super().__init__(name=name)
        self.force_field = force_field
        self.template_folder = template_folder
        self.batch_folder = batch_folder
        self.server_folder = server_folder
        self.in_file = in_file

    def create_sub_folder(self, temperature, pressure):
        """在batch_folder下创建pressure/temperature类的文件夹"""
        relative_path = os.path.join(self.force_field, str(pressure), str(temperature))
        folder = os.path.join(self.batch_folder, relative_path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        return (folder, relative_path)

    def copy_template(self, folder):
        """将template_folder中的文件复制到folder文件夹中"""
        for root, dirs, files in os.walk(self.template_folder):
            for file in files:
                shutil.copy(os.path.join(root, file), folder)

    def change_input_file(self, folder, pressure, temperature):
        """针对当前的folder，修改in文件"""
        with open(
            os.path.join(self.template_folder, self.in_file), "r"
        ) as template_input_file, open(
            os.path.join(folder, self.in_file), "w"
        ) as new_input_file:
            content = template_input_file.readlines()
            content[16] = re.sub("[0-9]+", str(temperature), content[17])
            content[17] = re.sub("[0-9]+", str(pressure), content[18])
            for line in content:
                new_input_file.write(line)

    def bsub_work(self, server_sub_folder, node, processor, new=True):
        """提交server_sub_folder中的in文件"""
        if new == True:
            self.run_shell(
                "cd {}; bsub -q q_x86_share -N {} -np {} -o out.log -i {} \
                /GFPS8p/caoby/software/lammps/lammps-stable_12Dec2018/src/lmp_mpi -sf opt".format(
                    server_sub_folder, node, processor, self.in_file
                )
            )
        else:
            self.run_shell(
                "cd {}; bsub -q q_x86_expr -N {} -np {} -o out.log -i {} lmp".format(
                    server_sub_folder, node, processor, self.in_file
                )
            )
