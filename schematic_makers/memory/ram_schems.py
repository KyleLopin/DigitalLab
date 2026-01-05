# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Schematic generator for a simple two-RAM tri-state bus topology.

This module uses Schemdraw to build an introductory memory subsystem
diagram: two RAM blocks (A and B) sharing a common DQ data bus via
tri-state buffers, connected to a single-bus CPU.

The intent is to provide a teaching-friendly schematic for explaining:

* Tri-state buffering on a shared data bus
* CPU read/write control (CE/OE/WE-style signals)
* How multiple memory devices can share a common bus

This is an initial, minimal example. More complete memory-system
variants (e.g., additional RAMs, address decoding, separate instruction
and data memories, etc.) are expected to be implemented in additional
functions or modules later.
"""

__author__ = "Kyle Vitautas Lopin"


# installed libaries
import schemdraw as sd
from schemdraw.elements import connectors, lines
import schemdraw.logic as logic

# local files
from schematic_makers.base import CPU_1Bus, RAM, RAMDown, CPU_L


def ram_1_tri_states(filename=None):
    """
    Draw a two-RAM tri-state bus schematic and optionally save it to a file.

    This helper constructs a Schemdraw Drawing showing:
      * Two RAMDown instances ("RAM A" and "RAM B")
      * Their data outputs and inputs gated by tri-state buffers
      * A shared DQ bus connecting both RAMs and a single-bus CPU
      * Control lines for chip enable (CE_A/CE_B), output enable (OE_A/OE_B),
        and write enable (WE_A/WE_B/WE_C)

    The function mutates the Schemdraw Drawing context in place and, if
    a filename is provided, writes the resulting schematic to disk.

    Parameters
    ----------
    filename : str or None, optional
        Output filename for the rendered schematic (e.g. "ram_bus.svg").
        If None, the drawing is not saved and is just displayed/returned
        by the caller's Drawing context.

    Returns
    -------
    None
        The function is called for its side effects on the Schemdraw
        Drawing and optional file output; it does not return a value.
    """
    with sd.Drawing() as d:
        rams = []
        # address_line = d.add(lines.Line().right(d.unit*0.02))
        # for ram_l, pt in [("A", address_line.start), ("B", address_line.end)]:
        ram = RAMDown("RAM A\n\n\n", size=(4, 4))
        # rams.append(ram)
        d.add(lines.Line().at(ram["CE"]).right(d.unit * 0.1).label(f"CE_A", loc="right"))
        d.add(lines.Line().at(ram["Data Out"]).down(d.unit * 0.25))
        tri_out = d.add(logic.Tristate(outputnot=False))
        d.add(lines.Line().at(tri_out.c).right(d.unit * 0.2).label(f"OE_A", loc="bottom"))
        print(dir(tri_out))
        print(tri_out.anchors)
        d.add(lines.Line().at(tri_out.out).down(d.unit * 0.1))
        tri_in = d.add(logic.Tristate(outputnot=False).at(ram["Data In"]).reverse())
        d.add(lines.Line().at(tri_in.c).right(d.unit * 0.01).label(f"WE_A", loc="right"))
        d.add(lines.Line().at(tri_in.end).toy(tri_out.end))
        d.add(connectors.BusLine().tox(tri_out.end))

        bus = d.add(connectors.BusLine().right(d.unit * 3.0).label(r"$\mathbf{DQ}$", loc="top", fontsize=20))
        # tri_wb = d.add(logic.Tristate(outputnot=False).up().flip())
        # d.add(lines.Line().at(tri_wb.c).right(d.unit * 0.01).label(f"WE_B", loc="right"))
        # d.add(lines.Line().at(tri_wb.out).up(d.unit * 0.35))
        # ram_b = d.add(RAMDown("RAM B\n\n\n", size=(4, 4)).anchor("Data In").right())
        # d.add(lines.Line().at(ram_b["CE"]).right(d.unit * 0.1).label(f"CE_B", loc="right"))
        # tri_rb = d.add(logic.Tristate(outputnot=False).at(ram_b["Data Out"]).down())
        # d.add(lines.Line().toy(tri_wb.start))
        # d.add(lines.Line().at(tri_rb.c).right(d.unit * 0.2).label(f"OE_B", loc="top", ofst=(0.3, 0.2)))

        # d.add(connectors.BusLine().at(bus.end).right(d.unit * 2))
        cpu = d.add(CPU_1Bus().anchor("DQ"))

        # region connect CPU
        tri_c = d.add(logic.Tristate(outputnot=False, controlnot=False).at(cpu["Write"]).left().flip())
        print("a: ", tri_c.__dict__)
        print("b: ", tri_c.__dict__.keys())
        d.add(connectors.BusLine().toy(bus.end))
        d.add(lines.Line().at(tri_c.c).up(d.unit * 0.01).label(f"OE_C", loc="right"))

        # add addr lines
        d.add(lines.Line().at(cpu.Addr).toy(ram.Addr))
        d.add(lines.Line().to(ram.Addr))
        # d.add(lines.Line().at(ram_b.Addr).toy(ram.Addr).dot())
        # endregion connect CPU

        if filename:
            d.save(filename)


def ram_2_tri_states(filename=None):
    """
    Draw a two-RAM tri-state bus schematic and optionally save it to a file.

    This helper constructs a Schemdraw Drawing showing:
      * Two RAMDown instances ("RAM A" and "RAM B")
      * Their data outputs and inputs gated by tri-state buffers
      * A shared DQ bus connecting both RAMs and a single-bus CPU
      * Control lines for chip enable (CE_A/CE_B), output enable (OE_A/OE_B),
        and write enable (WE_A/WE_B/WE_C)

    The function mutates the Schemdraw Drawing context in place and, if
    a filename is provided, writes the resulting schematic to disk.

    Parameters
    ----------
    filename : str or None, optional
        Output filename for the rendered schematic (e.g. "ram_bus.svg").
        If None, the drawing is not saved and is just displayed/returned
        by the caller's Drawing context.

    Returns
    -------
    None
        The function is called for its side effects on the Schemdraw
        Drawing and optional file output; it does not return a value.
    """
    with sd.Drawing() as d:
        rams = []
        # address_line = d.add(lines.Line().right(d.unit*0.02))
        # for ram_l, pt in [("A", address_line.start), ("B", address_line.end)]:
        ram = RAMDown("RAM A\n\n\n", size=(4, 4))
        # rams.append(ram)
        d.add(lines.Line().at(ram["CE"]).right(d.unit * 0.1).label(f"CE_A", loc="right"))
        d.add(lines.Line().at(ram["Data Out"]).down(d.unit * 0.25))
        tri_out = d.add(logic.Tristate(outputnot=False))
        d.add(lines.Line().at(tri_out.c).right(d.unit * 0.2).label(f"OE_A", loc="bottom"))
        print(dir(tri_out))
        print(tri_out.anchors)
        d.add(lines.Line().at(tri_out.out).down(d.unit * 0.1))
        tri_in = d.add(logic.Tristate(outputnot=False).at(ram["Data In"]).reverse())
        d.add(lines.Line().at(tri_in.c).right(d.unit * 0.01).label(f"WE_A", loc="right"))
        d.add(lines.Line().at(tri_in.end).toy(tri_out.end))
        d.add(connectors.BusLine().tox(tri_out.end))

        bus = d.add(connectors.BusLine().right(d.unit * 3.0).label(r"$\mathbf{DQ}$", loc="top", fontsize=20))
        tri_wb = d.add(logic.Tristate(outputnot=False).up().flip())
        d.add(lines.Line().at(tri_wb.c).right(d.unit * 0.01).label(f"WE_B", loc="right"))
        d.add(lines.Line().at(tri_wb.out).up(d.unit * 0.35))
        ram_b = d.add(RAMDown("RAM B\n\n\n", size=(4, 4)).anchor("Data In").right())
        d.add(lines.Line().at(ram_b["CE"]).right(d.unit * 0.1).label(f"CE_B", loc="right"))
        tri_rb = d.add(logic.Tristate(outputnot=False).at(ram_b["Data Out"]).down())
        d.add(lines.Line().toy(tri_wb.start))
        d.add(lines.Line().at(tri_rb.c).right(d.unit * 0.2).label(f"OE_B", loc="top", ofst=(0.3, 0.2)))

        d.add(connectors.BusLine().at(bus.end).right(d.unit * 2))
        cpu = d.add(CPU_1Bus().anchor("DQ"))

        # region connect CPU
        tri_c = d.add(logic.Tristate(outputnot=False, controlnot=False).at(cpu["Write"]).left().flip())
        print("a: ", tri_c.__dict__)
        print("b: ", tri_c.__dict__.keys())
        d.add(connectors.BusLine().toy(bus.end))
        d.add(lines.Line().at(tri_c.c).up(d.unit * 0.01).label(f"OE_C", loc="right"))

        # add addr lines
        d.add(lines.Line().at(cpu.Addr).toy(ram.Addr))
        d.add(lines.Line().to(ram.Addr))
        d.add(lines.Line().at(ram_b.Addr).toy(ram.Addr).dot())
        # endregion connect CPU

        if filename:
            d.save(filename)


def ram_4_bus(filename=None):
    with sd.Drawing() as d:
        # region draw RAMs
        rams = []  # is not needed?
        tris_outs = []
        ram_ls = ["A", "B", "C", "D"]
        ram_ls = ["A", "B"]
        seg = d.add(lines.Line().right(d.unit * 0.001))
        for i, ram_label in enumerate(ram_ls):
            if i < len(ram_ls):  # can try to put ram on bottom of bus but it screws up the label placement to flip the RAMs
                tri_out = d.add(logic.Tristate(outputnot=False).down().at(seg.end).anchor("end"))
                ram = RAMDown(f"RAM {ram_label}\n\n\n", size=(4, 4)).at(tri_out.start).anchor("Data Out").right()
                rams.append(ram)
                tris_outs.append(tri_out)
            # else:
            #     tri_out = d.add(logic.Tristate(outputnot=False).up().at(seg.end).anchor("end"))
            #     ram = RAMDown(f"RAM {ram_label}\n\n\n", size=(4, 4)).at(tri_out.start).anchor("Data Out").left()
            #     d.show()

            d.add(lines.Line().at(tri_out.c).left(d.unit * 0.1).label(f"OE_{ram_label}", loc="top", ofst=(-0.5, -0.1)))

            d.add(lines.Line().at(ram["CE"]).right(d.unit * 0.1).label(f"CE_{ram_label}", loc="top"))
            d.add(connectors.BusLine().at(tri_out.end).tox(ram["Data In"]))
            tri_in = d.add(logic.Tristate(outputnot=False).up().flip())
            d.add(lines.Line().at(tri_in.c).right(d.unit * 0.01).label(f"WE_A", loc="right"))
            if i < len(ram_ls)-1:
                seg = d.add(connectors.BusLine().at(tri_in.start).right(d.unit * 1.5))
        # endregion draw RAMs
        # region cpu
        bus_down = d.add(connectors.BusLine().at(tris_outs[1].end).down(d.unit * 1.5))
        d.add(connectors.BusLine().right(d.unit * 1.2))
        cpu = d.add(CPU_1Bus().anchor("DQ"))

        tri_we = d.add(logic.Tristate(outputnot=False, controlnot=True).at(cpu["Write"]).left().flip())
        d.add(lines.Line().up(d.unit*0.01).at(tri_we.c).label("OE#_CPU", loc="top"))
        d.add(connectors.BusLine().at(tri_we.end).tox(bus_down.end))

        d.add(lines.Line().at(cpu.Addr).tox(rams[0]["Data Out"]).color("green"))
        d.add(lines.Line().left(d.unit * 1).color("green"))
        d.add(lines.Line().toy(rams[0].Addr).color("green"))
        for ram in rams:
            d.add(lines.Line().tox(ram.Addr).color("green").dot())

        # endregion cpu
        if filename:
            d.save(filename)
        else:
            d.show()


def ram_4_addr_expand(filename=None):
    with sd.Drawing() as d:
        ram_ls = ["A", "B", "C", "D"]
        addr_last = None
        addr = d.add(lines.Line().right(d.unit * 0.1))
        rams = []
        save_lines = {}
        for i, ram_label in enumerate(ram_ls):
            # d.add(connectors.BusLine().at(seg.end).up(d.unit*1.5))
            ram = d.add(d.add(RAM(f"RAM {ram_label}\n\n\n\n\n").at(addr.end).anchor("Addr").right()))
            rams.append(ram)
            if i >= len(ram_ls) - 1:
                break

            addr_horizontal = d.add(lines.Line().at(addr.start).down(d.unit * 1.0))
            if i == 1:
                save_lines["Addr"] = addr_horizontal.end
            d.add(lines.Line().right(d.unit * 3).dot())
            d.add(lines.Line().up(d.unit * 1.0))
            addr = d.add(lines.Line().right(d.unit * 0.1))

        for i, pin in enumerate(["WE#", "OE#", "CE#"]):
            last = None
            for ram in rams:
                print("check")
                line = d.add(lines.Line().at(ram[pin]).down((i+1)*d.unit * 0.1))
                if last:
                    d.add(lines.Line().to(last).dot())
                last = line.end
            save_lines[pin] = last

        d.add(lines.Line().at(save_lines["Addr"]).down(d.unit * 1.5))
        d.add(lines.Line().right(d.unit * 0.7))
        cpu = d.add(CPU_L().anchor("Addr"))

        for i, pin in enumerate(["WE#", "OE#", "CE#"]):
            d.add(lines.Line().at(cpu[pin]).left((i+1) * d.unit * 0.1+0.3))
            d.add(lines.Line().toy(save_lines[pin]).dot())

        for i, ram in enumerate(rams):
            d.add(connectors.BusLine().at(ram["Data In"]).left(d.unit * 0.3))
            d.add(connectors.BusLine().down(d.unit * (1.6+i*0.1)))
            seg = d.add(connectors.BusLine().tox(ram["Data Out"]))
            d.add(connectors.BusLine().to(ram["Data Out"]))
            if i == 0:
                d.add(connectors.BusLine().at(seg.end).down(d.unit * 2.5))
                d.add(connectors.BusLine().tox(cpu["DQ[7:4]"]))
                d.add(connectors.BusLine().right(d.unit * 0.2))
                d.add(connectors.BusLine().toy(cpu["DQ[7:4]"]))
                d.add(connectors.BusLine().to(cpu["DQ[7:4]"]))
            elif i == 1:
                d.add(connectors.BusLine().at(seg.start).down(d.unit * 2.2))
                d.add(connectors.BusLine().tox(cpu["DQ[3:0]"]))
                d.add(connectors.BusLine().to(cpu["DQ[3:0]"]))
            elif i == 2:
                d.add(connectors.BusLine().at(seg.start).toy(cpu["DQ[15:12]"]))
                d.add(connectors.BusLine().to(cpu["DQ[15:12]"]))
            elif i == 3:
                d.add(connectors.BusLine().at(seg.start).toy(cpu["DQ[11:8]"]))
                d.add(connectors.BusLine().to(cpu["DQ[11:8]"]))
        if filename:
            d.save(filename)


if __name__ == '__main__':
    ram_1_tri_states(filename="ram_1_tri_states.svg")
    # ram_4_bus(filename="ram_2_bus.svg")
    # ram_4_addr_expand(filename="ram_4_to_16.svg")
