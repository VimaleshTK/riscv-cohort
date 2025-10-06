# UART and AXI Protocols

## UART (Universal Asynchronous Receiver-Transmitter)
UART is a serial communication protocol that allows two devices to exchange data.
It's one of the simplest and most common interfaces used in embedded systems for debugging, logging, and interfacing with peripherals like GPS modules or sensors.
Data is transmitted in frames. 


#### A standard UART frame consists of:

  * Start Bit: A single bit that transitions from high to low, signaling the beginning of a frame.

  * Data Bits: Typically 5 to 9 bits of the actual data, usually sent with the Least Significant Bit (LSB) first.
  
  * Parity Bit (Optional): Used for basic error checking. It can be set to even, odd, or none.
  
  * Stop Bit(s): One or two bits that transition from low to high, signaling the end of the frame.


Unlike synchronous protocols (like SPI or I2C), UART does not use a shared clock signal.
UART communication is full-duplex, meaning data can be sent and received simultaneously through separate transmit (Tx) and receive (Rx) lines.

## AXI (Advanced eXtensible Interface)
AXI is a high-performance, high-frequency bus protocol, part of the ARM **AMBA (Advanced Microcontroller Bus Architecture)** specification. It is designed to connect processors with memory controllers and other high-bandwidth peripherals within an SoC.
#### AXI communication occurs over five independent channels, which enables high throughput and low latency:
  * Write Address Channel (AW): Carries the address and control information for a write transaction.
  * Write Data Channel (W): Carries the actual data to be written.
  * Write Response Channel (B): Provides a response from the slave back to the master after a write is completed.
  * Read Address Channel (AR): Carries the address and control information for a read transaction.
  * Read Data Channel (R): Carries the read data from the slave back to the master.

