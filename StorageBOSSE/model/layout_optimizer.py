import os
import pandas as pd
import numpy as np
from StorageBOSSE.excelio.create_master_input_dict import XlsxReader
from LandBOSSE.landbosse.excelio.XlsxDataframeCache import XlsxDataframeCache
from StorageBOSSE.model.Manager import Manager
import xlsxwriter
from openpyxl import load_workbook

class layout_optimizer():
    """optimizes container layout"""
    def __init__(self, input_dict, output_dict):
        self.num_pad = output_dict['num_containers']
        self.pad_len = input_dict['container_length'] + 2 * input_dict['container_pad_buffer']
        self.pad_wid = input_dict['container_width'] + 2 * input_dict['container_pad_buffer']
        output_dict['pad_len'] = self.pad_len
        output_dict['pad_wid'] = self.pad_wid

    def create_layouts(self):
        """creates layouts for given nber of pads. Examines 1 to ceil(sqrt(num_pad)) rows, square or nearly square"""
        self.num_layouts = int(np.ceil(np.sqrt(self.num_pad)))
        self.num_full_row = np.linspace(1, self.num_layouts, self.num_layouts)  # nber of rows
        self.pad_per_row = np.zeros(self.num_layouts) # nber of pads per row
        self.row_len = np.zeros(self.num_layouts)
        if self.num_pad % 2 == 0:  # even
            self.num_full_row[0:2] = np.array([1, 2])
        else:  # odd
            self.num_full_row[0:2] = np.array([1, 1])
        self.pad_per_row[0:2] = np.array([self.num_pad, np.ceil(self.num_pad/2)])
        self.pad_per_row[2:]  = np.floor(self.num_pad/self.num_full_row[2:])
        self.num_left = self.num_pad - self.num_full_row*self.pad_per_row
        self.num_tot_row = self.num_full_row + np.where(self.num_left > 0.5, 1, 0)
        self.row_len = self.pad_per_row * self.pad_wid

    def minimize_AR(self):
        """ choose layout with minimum aspect ratio"""
        self.AR1 = (self.row_len + input_dict['road_width_m']) / (self.num_tot_row*self.pad_len + (np.floor(self.num_tot_row/2) + 1)*input_dict['road_width_m'])
        self.AR2 = 1/self.AR1
        self.AR3 = np.maximum(self.AR1, self.AR2)
        self.num_opt_AR = np.argmin(self.AR3)
        self.num_tot_row = self.num_tot_row[self.num_opt_AR]  # extract parameters of optimal layout
        self.num_full_row = self.num_full_row[self.num_opt_AR]
        self.pad_per_row = self.pad_per_row[self.num_opt_AR]
        self.num_left = self.num_left[self.num_opt_AR]

    def calc_road_len(self):
        """ calculate road length """
        self.road_grid_len = (self.row_len + input_dict['road_width_m'] + 2*self.pad_len)*(np.floor(self.num_tot_row/2) ) + self.row_len + input_dict['road_width_m']
        self.road_grid_len = np.where((self.num_tot_row % 2 == 0) & (self.num_left > 0.5), (self.road_grid_len - self.pad_wid * (self.pad_per_row - self.num_left)), self.road_grid_len)  # if even number of rows and last row is partial, subtract appropriate amount of road length
        self.road_grid_len = float(self.road_grid_len)

    def calc_cable_len(self):
        """ calcualted cable length within storage grid"""
        self.cable_grid_len = self.pad_len*self.num_tot_row + self.num_full_row*(self.row_len - self.pad_wid) + \
                              input_dict['road_width_m']*(np.ceil(self.num_tot_row/2) - 1) +  np.maximum(((self.num_left - 1) * self.pad_wid), 0)

    def run_module(self):
        """Runs the layout optimizer module"""
        if output_dict['num_containers'] == 1:
            input_dict['layout'] = 'linear'
        if input_dict['layout'] == 'linear':
            self.cable_grid_len = output_dict['num_containers'] * \
                                        (input_dict['container_width'] + 2 * input_dict['container_pad_buffer'])
            self.road_grid_len = self.cable_grid_len
            self.num_tot_row = 1
            self.num_full_row = 1
            self.pad_per_row = self.num_pad
            self.num_left = 0
            self.num_opt_AR = 1
        elif input_dict['layout'] == 'aspect ratio optimized':
            self.create_layouts()
            self.minimize_AR()
            self.calc_cable_len()
            self.calc_road_len()
            self.cable_grid_len = self.cable_grid_len # optimal layout length
            self.road_grid_len = self.road_grid_len
        else:
            self.num_full_row = input_dict['layout'][0]
            self.pad_per_row = input_dict['layout'][1]
            self.num_left = input_dict['layout'][2]
            if self.num_left == 0:
                self.num_tot_row = self.num_full_row
            else:
                self.num_tot_row = self.num_full_row + 1
            self.row_len = self.pad_per_row * self.pad_wid
            self.calc_cable_len()
            self.calc_road_len()
            self.num_opt_AR = 1
        output_dict['num_tot_row'] = self.num_tot_row
        output_dict['num_full_row'] = self.num_full_row
        output_dict['pad_per_row'] = self.pad_per_row
        output_dict['num_left'] = self.num_left
        output_dict['cable_grid_len'] = self.cable_grid_len
        output_dict['road_grid_len'] = self.road_grid_len

input_dict = {'container_length': 8,
              'container_width': 3,
              'container_pad_buffer': 1,
              'road_width_m': 5,
              'layout': 'linear'
              }
output_dict = {'num_containers': 10}
opt = layout_optimizer(input_dict, output_dict)
opt.run_module()
x=0
