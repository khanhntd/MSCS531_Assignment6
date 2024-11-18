import os
import m5
from m5.objects import *

# Create the system
system = System()
system.clk_domain = SrcClockDomain(clock="2GHz", voltage_domain=VoltageDomain())
system.mem_mode = "timing"  # Use timing memory mode
system.mem_ranges = [AddrRange("8GB")]  # Updated to match DRAM capacity

# Create 4 CPUs
num_cores = 4
system.cpu = [X86MinorCPU() for _ in range(num_cores)]

# Create caches for each CPU
for cpu in system.cpu:
    cpu.icache = Cache(
        size='128kB',
        assoc=4,
        tag_latency=2,
        data_latency=2,
        response_latency=1,
        mshrs=16,
        tgts_per_mshr=4
    )
    cpu.dcache = Cache(
        size='128kB',
        assoc=4,
        tag_latency=2,
        data_latency=2,
        response_latency=1,
        mshrs=16,
        tgts_per_mshr=4
    )
    # Connect caches to CPU
    cpu.icache_port = cpu.icache.cpu_side
    cpu.dcache_port = cpu.dcache.cpu_side

# Create a memory bus
system.membus = SystemXBar()

# Connect CPU caches to memory bus
for cpu in system.cpu:
    cpu.icache.mem_side = system.membus.cpu_side_ports
    cpu.dcache.mem_side = system.membus.cpu_side_ports

# Create a memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8(device_size="512MB")  # Set correct device size
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.master

# Create the workload
process = Process()
thispath = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(
    thispath,
    "./daxpy-static",
)
process.cmd = [bin_path]
system.workload = SEWorkload.init_compatible(bin_path)

# Assign workload to all CPUs
for cpu in system.cpu:
    cpu.workload = process
    cpu.createThreads()
    cpu.createInterruptController()

    for i in range(len(cpu.interrupts)):
        cpu.interrupts[i].pio = system.membus.mem_side_ports
        cpu.interrupts[i].int_requestor = system.membus.cpu_side_ports
        cpu.interrupts[i].int_responder = system.membus.mem_side_ports

# Set up the system root
root = Root(full_system=False, system=system)
m5.instantiate()

# Run the simulation
print("Starting simulation...")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")