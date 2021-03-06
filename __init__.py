#    sumelim - bqcsv action module that eliminates rows or columns from a 
#    CSV file based on whether or not the contents sum to a given threshold 
#
#    Copyright (C) 2017 Winslow Williams 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx
from csvdb import csvmemory
from actions import utils

BOX_SPACER = 5
STR_ROWS = "Rows"
STR_COLS = "Columns"

class SumElimDialog(wx.Dialog):

  def __init__(self,parent,table):
    wx.Dialog.__init__(self,parent)

    self.table = table
    self.threshold = 0
    self.roc = 0
    self.initUI()
    self.SetSize((320,240))
    self.SetTitle("SumElim")

  def initUI(self):
    vbox = wx.BoxSizer(wx.VERTICAL)

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    x = wx.StaticText(self,-1,"Threshold")
    hbox.AddSpacer(BOX_SPACER)
    hbox.Add(x)
    hbox.AddSpacer(BOX_SPACER)
    self.threshold_ctrl = wx.TextCtrl(self)
    self.threshold_ctrl.SetEditable(True)
    self.threshold_ctrl.AppendText(str(self.threshold))
    hbox.AddSpacer(BOX_SPACER)
    hbox.Add(self.threshold_ctrl)
    hbox.AddSpacer(BOX_SPACER)
    vbox.Add(hbox);

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    x = wx.StaticText(self,-1,"")
    hbox.AddSpacer(BOX_SPACER)
    hbox.Add(x)
    hbox.AddSpacer(BOX_SPACER)
    self.roc_ctrl = wx.ComboBox(self,style=wx.CB_DROPDOWN,choices=[STR_ROWS,STR_COLS])
    self.roc_ctrl.SetEditable(False)
    self.roc_ctrl.SetStringSelection('Rows')
    hbox.AddSpacer(BOX_SPACER)
    hbox.Add(self.roc_ctrl)
    hbox.AddSpacer(BOX_SPACER)
    vbox.Add(hbox);

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    self.ok_button = wx.Button(self,wx.ID_OK)
    hbox.AddSpacer(BOX_SPACER)
    hbox.Add(self.ok_button)
    hbox.AddSpacer(BOX_SPACER)
    self.cancel_button = wx.Button(self,wx.ID_CANCEL)
    hbox.AddSpacer(BOX_SPACER)
    hbox.Add(self.cancel_button)
    hbox.AddSpacer(BOX_SPACER)
    vbox.Add(hbox)

    self.ok_button.Bind(wx.EVT_BUTTON,self.onOK)
    self.cancel_button.Bind(wx.EVT_BUTTON,self.onCancel)

    self.SetSizer(vbox)

  def getThreshold(self):
    return self.threshold

  def getRowsOrColumns(self):
    return self.roc

  def onOK(self,event):
    self.roc = self.roc_ctrl.GetCurrentSelection()
    self.threshold = float(self.threshold_ctrl.GetValue())
    self.EndModal(wx.ID_OK)

  def onCancel(self,event):
    self.EndModal(wx.ID_CANCEL)


class SumElimPlugin(object):

  def __init__(self,parent_frame):
    self.path = None
    self.parent_frame = parent_frame
 
  def getLabel(self):
    '''
    Required
    '''
    return 'Sum Elim'

  def getDescription(self):
    '''
    Required
    '''
    return 'Perform a natural join between two .csv files'

  def setPath(self,v):
    self.path = v

  def doAction(self,table):
    '''
    Required
    '''
    if None is table:
      dialog = SumElimDialog(self.parent_frame,table)
      chk = dialog.ShowModal()
      if wx.ID_OK == chk:
        threshold = dialog.getThreshold()
        roc = dialog.getRowsOrColumns()
        memw = csvmemory.MemoryWriter()

        # rows
        if 0 == roc:
          memw.setHeader(table.getHeader())
          for row in table.getIter():
            summ = 0.0
            for col in row:
              try:
                summ += float(col) 
              except ValueError as ex:
                # If it isn't a number, just skip it
                pass 
            if summ >= threshold:
              memw.appendRow(row)
        # columns
        else:
          msg = 'Columns' 
          wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)
          sums = list()
          header = list()
          for v in table.getHeader():
            sums.append(0.0)
          for row in table.getIter():
            idx = 0
            for col in row:
              try:
                sums[idx] += float(col)
              except ValueError as ex:
                # If it isn't a number, make a large contribution 
                sums[idx] += 1000000 
              idx += 1

          table.reset()
          header = list()
          idx = 0
          for v in table.getHeader():
            if sums[idx] >= threshold:
              header.append(v) 
            idx += 1 
          memw.setHeader(header)
          for row in table.getIter():
            idx = 0
            output_row = list()
            for col in row:
              if sums[idx] >= threshold:
                output_row.append(col)
              idx += 1
            memw.appendRow(output_row)  
          
        path = utils.getTempFilename()
        memw.save(path)
        self.parent_frame.addPage(path,delete_on_exit=True)

def getPlugin(parent_frame):
  return SumElimPlugin(parent_frame)
