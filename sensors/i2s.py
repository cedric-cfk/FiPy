# The MIT License (MIT)
# Copyright (c) 2019 Michael Shi
# Copyright (c) 2020 Mike Teachman
# https://opensource.org/licenses/MIT

# Purpose:
# - read 32-bit audio samples from the left channel of an I2S microphone
# - snip upper 16-bits from each 32-bit microphone sample
# - write 16-bit samples to a SD card file using WAV format
#
# Recorded WAV file is named:
#   "mic_left_channel_16bits.wav"
#
# Hardware tested:
# - INMP441 microphone module
# - MSM261S4030H0 microphone module

import os
import ulab as np
from machine import Pin
from machine import SD
from machine import I2S
from ulab import fft



class I2S:
    def __init__(self, bck, ws, sdin, record_time_in_seconds=1, sample_rate_in_Hz=12050):
        #======= USER CONFIGURATION =======
        sample_size_in_bits = 32
        sample_size_in_bytes = sample_size_in_bits // 8
        self.mic_sample_buffer_size_in_bytes = 4096
        self.num_sample_bytes_to_write = record_time_in_seconds * sample_rate_in_Hz * sample_size_in_bytes
        num_samples_in_dma_buffer = 256

        # I2S pins
        bck_pin = Pin(bck)
        ws_pin = Pin(ws)
        sdin_pin = Pin(sdin)

        self.audio_in = I2S(
            I2S.NUM0,
            bck=bck_pin, ws=ws_pin, sdin=sdin_pin,
            standard=I2S.PHILIPS,
            mode=I2S.MASTER_RX,
            dataformat=I2S.B32,
            channelformat=I2S.ONLY_LEFT,
            samplerate=sample_rate_in_Hz,
            dmacount=50,
            dmalen=num_samples_in_dma_buffer
        )

        # configure SD card
        #   slot=2 configures SD card to use the SPI3 controller (VSPI), DMA channel = 2
        #   slot=3 configures SD card to use the SPI2 controller (HSPI), DMA channel = 1
        self.sd = SD()
        os.mount(sd, "/sd")

        # create audio dir in case it does not exist
        try:
            os.stat('/sd/audio')
        except:
            os.mkdir('/sd/audio')

    # snip_16_mono():  snip 16-bit samples from a 32-bit mono sample stream
    # assumption: I2S configuration for mono microphone.  e.g. I2S channelformat = ONLY_LEFT or ONLY_RIGHT
    # example snip:
    #   samples_in[] =  [0x44, 0x55, 0xAB, 0x77, 0x99, 0xBB, 0x11, 0x22]
    #   samples_out[] = [0xAB, 0x77, 0x11, 0x22]
    #   notes:
    #       samples_in[] arranged in little endian format:
    #           0x77 is the most significant byte of the 32-bit sample
    #           0x44 is the least significant byte of the 32-bit sample
    #
    # returns:  number of bytes snipped
    def snip_16_mono(samples_in, samples_out):
        num_samples = len(samples_in) // 4
        for i in range(num_samples):
            samples_out[2*i] = samples_in[4*i + 2]
            samples_out[2*i + 1] = samples_in[4*i + 3]

        return num_samples * 2

    def read_fft(self):
        txt = open('/sd/audio/recording-to-fft.txt','wb')
        #txt = open('/sd/audio/recording-to-fft.txt','w')

        # allocate sample arrays
        #   memoryview used to reduce heap allocation in while loop
        mic_samples = bytearray(self.mic_sample_buffer_size_in_bytes)
        mic_samples_mv = memoryview(mic_samples)

        num_sample_bytes_written = 0

        print('starting...')

        # read 32-bit samples from I2S microphone, snip upper 16-bits, write snipped samples to WAV file
        while num_sample_bytes_written < self.num_sample_bytes_to_write:
            try:
                # try to read a block of samples from the I2S microphone
                # readinto() method returns 0 if no DMA buffer is full
                num_bytes_read_from_mic = audio_in.readinto(mic_samples_mv, timeout=0)

                if num_bytes_read_from_mic > 0:
                    #calculate fft
                    real, imaginary = fft.fft(np.array(list(mic_samples_mv[:num_bytes_read_from_mic])))
                    #write fft samples to txt (just for test reasons. Later store and send data to Beep)
                    txt.write(real)
                    txt.write(imaginary)
                    #txt.write('\n\nreal part:\t' + str(list(real)))
                    #txt.write('\nimaginary part:\t' + str(list(imaginary)))
                    num_sample_bytes_written += num_bytes_read_from_mic
            except (KeyboardInterrupt, Exception) as e:
                print('caught exception {} {}'.format(type(e).__name__, e))
                break

        txt.close()
        # do not unmount and deinit SD in case you want to read files via WiFi and a FTP connection
        #os.umount("/sd")
        #sd.deinit()

        # do not deinit audio in case you will record an other round
        #audio_in.deinit()
        print('#'+str(i)+' ... done! -- %d sample bytes written to txt file' % num_sample_bytes_written)
        print()


    print('All done!')
