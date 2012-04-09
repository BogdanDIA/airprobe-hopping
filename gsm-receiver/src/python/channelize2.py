#!/usr/bin/env python
#
# Copyright 2009 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, blks2
import os, time
import scipy, pylab
from scipy import fftpack
from pylab import mlab
from gnuradio.eng_option import eng_option
from optparse import OptionParser

class pfb_top_block(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        #parse the options
        parser = OptionParser(option_class=eng_option)
        parser.add_option("--inputfile", type="string", default="out/out.cf", help="set the input file")
        parser.add_option("--arfcn", type="int", default="40", help="set center ARFCN")
        parser.add_option("--srate", type="int", default="10000000", help="set sample frequency")
        parser.add_option("--decimation", type="int", default="17", help="decimation")
        parser.add_option("--nchannels", type="int", default="50", help="number of channels")
        parser.add_option("--nsamples", type="int", default="1280000", help="number of samples")
        (options, args) = parser.parse_args ()

        self._output_rate = options.srate / options.decimation

        # Create a set of taps for the PFB channelizer
        self._taps = gr.firdes.low_pass_2(1, options.srate, 145e3, 10e3, 
                                          attenuation_dB=100, window=gr.firdes.WIN_BLACKMAN_hARRIS)

        # Calculate the number of taps per channel for our own information
        tpc = scipy.ceil(float(len(self._taps)) /  float(options.nchannels))
        print "Number of taps:     ", len(self._taps)
        print "Number of channels: ", options.nchannels
        print "Taps per channel:   ", tpc

        self._o = float (options.nchannels) / float (options.decimation);
        print "pfb oversampling: ", self._o
        
        self.head = gr.head(gr.sizeof_gr_complex, options.nsamples)

        # Construct the channelizer filter
        self.pfb = blks2.pfb_channelizer_ccf(options.nchannels, self._taps, self._o)

        # Construct a vector sink for the input signal to the channelizer
        self.snk_i = gr.vector_sink_c()
        self.input = gr.file_source(gr.sizeof_gr_complex, "./out/out.cf", False);
        # Connect the blocks
        self.connect(self.input, self.head, self.pfb)

        self.output_files = list();
        for i in xrange(int(options.nchannels / 2) + 1):
          self.output_files.append(gr.file_sink(gr.sizeof_gr_complex, "./out/out_" + str(options.arfcn + i) + ".cf"))

        if (options.nchannels % 2) != 0:
          ind = 1;
        else:
          ind = 0
	
        for i in xrange(1, int(options.nchannels / 2) + ind):
          self.output_files.append(gr.file_sink(gr.sizeof_gr_complex, "./out/out_" + str(options.arfcn - int(options.nchannels / 2) - ind + i) + ".cf"))

        # Create a vector sink for each of nchannels output channels of the filter and connect it
        self.snks = list()
        for i in xrange(options.nchannels):
            self.snks.append(gr.vector_sink_c())
            self.connect((self.pfb, i), self.output_files[i])

def main():

    tstart = time.time()
    
    tb = pfb_top_block()
    tb.run()

    tend = time.time()
    print "Run time: %f" % (tend - tstart)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    
