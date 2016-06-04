'''
Created on Apr 20, 2016

@author: yanz3
'''
import subprocess
print ("hello world!")

management_permissions = 'Datastore.AllocateSpace,Datastore.Browse,Datastore.DeleteFile,Datastore.FileManagement,Datastore.UpdateVirtualMachineFiles,Global.Diagnostics,Global.Settings,Host.Config.Maintenance,Host.Config.NetService,Host.Config.Network,Host.Config.Power,Host.Config.Settings,Host.Config.Storage,Host.Config.SystemManagement,Host.Inventory.EditCluster,Network.Assign,Resource.ColdMigrate,Resource.HotMigrate,System.Anonymous,System.Read,System.View,VApp.ExtractOvfEnvironment,VApp.Import,VApp.ApplicationConfig,VirtualMachine.Config.AddNewDisk,VirtualMachine.Config.AdvancedConfig,VirtualMachine.Config.RemoveDisk,VirtualMachine.Config.Settings,VirtualMachine.Config.Unlock,VirtualMachine.GuestOperations.Query,VirtualMachine.GuestOperations.Modify,VirtualMachine.GuestOperations.Execute,VirtualMachine.GuestOperations.QueryAliases,VirtualMachine.GuestOperations.ModifyAliases,VirtualMachine.Interact.AnswerQuestion,VirtualMachine.Interact.ConsoleInteract,VirtualMachine.Interact.DeviceConnection,VirtualMachine.Interact.GuestControl,VirtualMachine.Interact.PowerOff,VirtualMachine.Interact.PowerOn,VirtualMachine.Interact.SetCDMedia,VirtualMachine.Inventory.Delete,VirtualMachine.Inventory.Unregister,VirtualMachine.State.CreateSnapshot,VirtualMachine.State.RemoveSnapshot'
print management_permissions.split(',')

uuid_sh_str = "grep 'data.uuid' /Users/yanz3/runtime.properties  | awk -F '=' '{print $2}'"
uuid = subprocess.check_output(uuid_sh_str, shell=True)#, stdout=subprocess.PIPE)
print uuid

s = "Management Network-94f23197-731d-4a22-a468-2cd68ccd1b18="
b = "94f23197-731d-4a22-a468-2cd68ccd1b18"
re = s.find("ts")
print s
print b
print type(s)
if b not in s:
    print "No 'is' here!"
else:
    print "Found 'is' in the string."

