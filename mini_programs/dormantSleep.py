# Raspberry Pico micropython low-power workaround
# Copyright (C) 2021 Tom Jorquera
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from machine import Pin
import lowpower

DORMANT_PIN = 15
btn = Pin(DORMANT_PIN, Pin.IN, Pin.PULL_DOWN)
btn.irq(lambda e: print("button event!"),
        Pin.IRQ_RISING)

lowpower.dormant_until_pin(DORMANT_PIN)
