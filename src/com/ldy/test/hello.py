'''
Created on Apr 20, 2016

@author: yanz3
'''

print ("hello world!")

management_permissions = 'Datastore.AllocateSpace,Datastore.Browse,Datastore.DeleteFile,Datastore.FileManagement,Datastore.UpdateVirtualMachineFiles,Global.Diagnostics,Global.Settings,Host.Config.Maintenance,Host.Config.NetService,Host.Config.Network,Host.Config.Power,Host.Config.Settings,Host.Config.Storage,Host.Config.SystemManagement,Host.Inventory.EditCluster,Network.Assign,Resource.ColdMigrate,Resource.HotMigrate,System.Anonymous,System.Read,System.View,VApp.ExtractOvfEnvironment,VApp.Import,VApp.ApplicationConfig,VirtualMachine.Config.AddNewDisk,VirtualMachine.Config.AdvancedConfig,VirtualMachine.Config.RemoveDisk,VirtualMachine.Config.Settings,VirtualMachine.Config.Unlock,VirtualMachine.GuestOperations.Query,VirtualMachine.GuestOperations.Modify,VirtualMachine.GuestOperations.Execute,VirtualMachine.GuestOperations.QueryAliases,VirtualMachine.GuestOperations.ModifyAliases,VirtualMachine.Interact.AnswerQuestion,VirtualMachine.Interact.ConsoleInteract,VirtualMachine.Interact.DeviceConnection,VirtualMachine.Interact.GuestControl,VirtualMachine.Interact.PowerOff,VirtualMachine.Interact.PowerOn,VirtualMachine.Interact.SetCDMedia,VirtualMachine.Inventory.Delete,VirtualMachine.Inventory.Unregister,VirtualMachine.State.CreateSnapshot,VirtualMachine.State.RemoveSnapshot'
print management_permissions.split(',')