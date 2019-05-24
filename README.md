PyOBD
======

PyOBD is an automotive diagnostic tool written entirely
in [Python](https://www.python.org). PyOBD will interface
with your automobile's OBD-II diagnostic port with an
[ELM-32x](https://www.elmelectronics.com/products/ics/obd/)
OBD to RS232 Interpreter.

What Can PyOBD Do?
------------------
The following features are currently implemented in PyOBD:
- Communicate with vehicles that support OBD-II (newer
  than 1996)
- Display results of vehicle emissions self tests.
- Read and clear diagnostic trouble codes from vehicle's
  emmissions control system.
- Display live emissions related data, such fuel trim,
  engine RPM, vehicle speed, etc.

What *Can't* PyOBD Do?
----------------------
The following features are not currently available but
may be implemented in future versions:
- Graph live data from vehicle sensors.
- Record and save live data from vehicle sensors.
- Display vendor specific live data.
- Read and clear diagnostic trouble codes from other
  vehicle components (ABS, power steering, etc.).

PyOBD Source
------------
The latest source code for PyOBD can be downloaded
from <https://github.com/beardedone55/pyobd/>.

Copyright and License
---------------------
Copyright 2004 Donour Sizemore <donour@uchicago.edu>
Copyright 2009 Secons Ltd. <http://www.obdtester.com>
Copyright 2019 Brian LePage <https://github.com/beardedone55/>

PyOBD is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later
version.

PyOBD is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
the GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with PyOBD; if not, see
<https://www.gnu.org/licenses/>.
