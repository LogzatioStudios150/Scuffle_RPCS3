import string
import AddressMap
from enum import Enum
from ByteTools import *
import ModuleEnumerator
import PIDSearcher
import GameplayEnums
import MovelistParser
from MovelistEnums import *
from threading import Thread



class SC6GameReader:
        def __init__(self):
            self.pid = -1
            self.process_handle = None
            self.test_block = 0
            self.primary_snapshots = []
            self.secondary_snapshots = []
            self.p1_movelist = None
            self.last_p1_movelist_address = None
            self.p2_movelist = None
            self.last_p2_movelist_address = None
            self.timer = 0
            self.do_write_movelist = False
            self.do_fix_goto = True
            self.is_movelist_new = False
            self.consecutive_frames_of_zero_timer = 0
            self.game = None
            
            #self.module_address = 0x140000000 #hard coding this until it breaks, then use ModuleEnumerator again
            #self.module_address = 0x7FF60AC30000 #new hardcoded
            
            self.game_module_address = 0

        def IsForegroundPID(self):
            pid = c.wintypes.DWORD()
            active = c.windll.user32.GetForegroundWindow()
            active_window = c.windll.user32.GetWindowThreadProcessId(active, c.byref(pid))
            return pid.value == self.pid

        def GetWindowRect(self):
            # see https://stackoverflow.com/questions/21175922/enumerating-windows-trough-ctypes-in-python for clues for doing this without needing focus using WindowsEnum
            if self.IsForegroundPID():
                rect = c.wintypes.RECT()
                c.windll.user32.GetWindowRect(c.windll.user32.GetForegroundWindow(), c.byref(rect))
                return rect
            else:
                return None

        def HasWorkingPID(self):
            return self.pid > -1

        def VoidPID(self):
            self.pid = -1

        def VoidMovelists(self):
            self.p1_movelist = None
            self.last_p1_movelist_address = None
            self.p2_movelist = None
            self.last_p2_movelist_address = None

        def MarkMovelistAsOld(self):
            self.is_movelist_new = False

        def HasNewMovelist(self):
            return self.is_movelist_new


        def UpdateCurrentSnapshot(self):
            if not self.HasWorkingPID():
                self.pid = PIDSearcher.GetPIDByName(b'rpcs3.exe')
                if self.HasWorkingPID():
                    if self.game != None:
                        self.process_handle = OpenProcess(0x10 | 0x20 | 0x08, False, self.pid) #0x10 = ReadProcess Privleges 0x20 = WriteProcess Privleges 0x08 = Operation Privleges
                        self.base_module_address = ModuleEnumerator.GetModuleAddressByPIDandName(pid = self.pid, name = "rpcs3.exe")
                        self.game_module_address = 0x300000000
                        # for game in Game:
                        #     for id in game.value:
                        #         if self.game_serial == id:
                        #             self.game = game
                        #             break
                        if self.game_module_address != None and self.game != None:
                            try:
                                self.test_block = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p1_guard_damage_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_global_timer_address)
                            except:
                                print("Game is set but isn't running.")
                        else:
                            self.test_block = 0

                    print("RPCS3 process id acquired: {}".format(self.pid))
                else:
                    print("Failed to find processid. Trying to acquire...")

            elif self.HasWorkingPID():
                if self.game != None:
                    if self.test_block == 0: #not in a fight yet or application closed
                        self.consecutive_frames_of_zero_timer += 1
                        if self.consecutive_frames_of_zero_timer > 10:
                            self.VoidPID()
                            self.VoidMovelists()
                        return False
                    else:
                        
                            

                        self.consecutive_frames_of_zero_timer = 0
                        if self.p1_movelist == None:
                            #movelist_sample = GetValueFromAddress(process_handle, AddressMap.p1_movelist_address, isString=True)
                            if self.game == Game.SCIV:
                                p1_movelist_address = AddressMap.SCIV_p1_movelist_address
                                p2_movelist_address = AddressMap.SCIV_p2_movelist_address
                            else:
                                p1_movelist_address = AddressMap.SCV_p1_movelist_address
                                p2_movelist_address = AddressMap.SCV_p2_movelist_address

                            movelist_sample = GetDataBlockAtEndOfPointerOffsetList(self.process_handle, self.game_module_address, [p1_movelist_address], 0x4)
                            movelist_sample = GetValueFromDataBlock(movelist_sample, 0)

                            if  movelist_sample == MovelistParser.Movelist.STARTER_INT:
                                #p1_movelist_address = GetValueFromAddress(self.process_handle, self.game_module_address + p1_movelist_address)
                                #p1_movelist_data = GetBlockOfData(self.process_handle, self.game_module_address + p1_movelist_address, AddressMap.MOVELIST_BYTES)
                                p1_movelist_data = GetDataBlockAtEndOfPointerOffsetList(self.process_handle, self.game_module_address, [p1_movelist_address], AddressMap.MOVELIST_BYTES)
                                #p2_movelist_address = GetValueFromAddress(self.process_handle, self.game_module_address + p2_movelist_address)
                                #p2_movelist_data = GetBlockOfData(self.process_handle, self.game_module_address + p2_movelist_address, AddressMap.MOVELIST_BYTES)
                                p2_movelist_data = GetDataBlockAtEndOfPointerOffsetList(self.process_handle, self.game_module_address, [p2_movelist_address], AddressMap.MOVELIST_BYTES)
                                self.p1_movelist = MovelistParser.Movelist(p1_movelist_data, 'p1', self.game, 0x04 if self.game == Game.SCV else 0x02)
                                self.p2_movelist = MovelistParser.Movelist(p2_movelist_data, 'p2', self.game, 0x04 if self.game == Game.SCV else 0x02)
                                self.is_movelist_new = True    
                            else:
                                self.is_movelist_new = False
                                return False

                        new_timer = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_global_timer_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_global_timer_address)

                        if self.timer == new_timer:
                            return False
                        else:
                            self.timer = new_timer

                        


                        #p1_startup_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p1_startup_block_breadcrumb, 0x100)
                        #p2_startup_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p2_startup_block_breadcrumb, 0x100)

                        #p1_movement_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p1_movement_block_breadcrumb, 0x100)
                        #p2_movement_block = GetDataBlockAtEndOfPointerOffsetList(process_handle, self.module_address, AddressMap.p2_movement_block_breadcrumb, 0x100)

                        p1_primary_move_id = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p1_move_id_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p1_primary_move_id_address, is_short =True)
                        p2_primary_move_id = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p2_move_id_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p2_primary_move_id_address, is_short=True)

                        p1_secondary_move_id = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p1_move_id_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p1_secondary_move_id_address, is_short =True)
                        p2_secondary_move_id = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p2_move_id_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p2_secondary_move_id_address, is_short =True)
                        
                        p1_gdam = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p1_guard_damage_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p1_guard_damage_address, is_short=True)
                        p2_gdam = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p2_guard_damage_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p2_guard_damage_address, is_short=True)

                        p1_input = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p1_input_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p1_input_address, is_short=True)
                        p1_global = SC6GlobalBlock(p1_input)

                        p2_input = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p2_input_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p2_input_address, is_short=True)
                        p2_global = SC6GlobalBlock(p2_input)

                        primary_value_p1 = PlayerSnapshot(self.p1_movelist, p1_gdam, p1_primary_move_id, p1_global)
                        secondary_value_p1 = PlayerSnapshot(self.p1_movelist, p1_gdam, p1_secondary_move_id, p1_global)
                        primary_value_p2 = PlayerSnapshot(self.p2_movelist, p2_gdam, p2_primary_move_id, p2_global)
                        secondary_value_p2 = PlayerSnapshot(self.p2_movelist, p2_gdam, p2_secondary_move_id, p2_global)
                        
                        p1_movelist_address = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p1_movelist_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p1_movelist_address)

                        if p1_movelist_address != self.last_p1_movelist_address:
                            self.p1_movelist = None
                            self.last_p1_movelist_address = None
                            self.VoidPID()

                        if self.do_write_movelist:
                            p1_movelist_address = GetValueFromAddress(self.process_handle, self.game_module_address + AddressMap.SCIV_p1_movelist_address if self.game == Game.SCIV else self.game_module_address + AddressMap.SCV_p1_movelist_address)
                            WriteBlockOfData(self.process_handle, self.game_module_address + p1_movelist_address, self.p1_movelist.generate_modified_movelist_bytes(self.do_fix_goto))
                            self.do_write_movelist = False
                            self.VoidPID()
                            self.VoidMovelists()
                            
                            
                        self.last_p1_movelist_address = p1_movelist_address
                            

                        self.primary_snapshots.append(GameSnapshot(primary_value_p1, primary_value_p2, self.timer))
                        self.secondary_snapshots.append(GameSnapshot(secondary_value_p1, secondary_value_p2, self.timer))
                        MAX_FRAMES_TO_KEEP = 1000
                        if len(self.primary_snapshots) > MAX_FRAMES_TO_KEEP:
                            self.primary_snapshots = self.primary_snapshots[MAX_FRAMES_TO_KEEP // 2: -1]
                        if len(self.secondary_snapshots) > MAX_FRAMES_TO_KEEP:
                            self.secondary_snapshots = self.secondary_snapshots[MAX_FRAMES_TO_KEEP // 2: -1]
                        return True
                    



class SC6MovementBlock:
    def __init__(self, move_id):
        self.movelist_id = move_id

class SC6StartupBlock:
    def __init__(self, gdam):
        self.guard_damage = gdam

class SC6GlobalBlock:
    def __init__(self, input_short):
        left_bytes = (input_short & 0xFF00) >> 8
        right_bytes = input_short & 0x00FF

        self.input_code_button = right_bytes
        self.input_code_direction = left_bytes

    def __repr__(self):
        repr = "{} | {} |".format(
            self.input_code_button, self.input_code_direction)
        return repr

class PlayerSnapshot:
    def __init__(self, movelist, gdam, move_id, global_block : SC6GlobalBlock):
        self.movelist = movelist
        self.movement_block = SC6MovementBlock(move_id)
        self.startup_block = SC6StartupBlock(gdam)
        self.global_block = global_block

class GameSnapshot:
    def __init__(self, p1_snapshot : PlayerSnapshot, p2_snapshot : PlayerSnapshot, timer):
        self.timer = timer
        self.p1 = p1_snapshot
        self.p2 = p2_snapshot

    def __repr__(self):
        return "{} ||| {}".format(self.p1, self.p2)


if __name__ == "__main__":
    import time
    import GameplayEnums
    myReader = SC6GameReader()
    old_state = None
    while True:
        successful_update = myReader.UpdateCurrentSnapshot()

        if successful_update:
            new_state = myReader.primary_snapshots[-1]
            print("you're open {}".format(new_state.timer))

        time.sleep(.005)

