#! /usr/bin/python
''' Class that represents a trace file '''
class Trace(object) :
	trace_file=""
	start_time=-1;
	end_time=-1;
	trace_in_mem=[];
	def __init__(self,trace_file) : 
		self.trace_file=trace_file;
		fh=open(self.trace_file,"r");
		for line in fh.readlines() :
			if( self.start_time == -1) :
				self.start_time=float(line.split(',')[1])/1000.0;
			self.end_time=float(line.split(',')[1])/1000.0;
			self.trace_in_mem+=[line]

	def calc_length(self) :
		return self.end_time-self.start_time

	def rewrite_trace_file(self,start,end) :
		fh=open("result.out","a");
		time_written_out=start
		print "start of new activity is ",start, " and end is ",end
		while ( time_written_out < end ) :
			''' write out the list to a file in epochs until exhausted '''
			epoch_start=time_written_out
			epoch_end  =min(time_written_out+self.calc_length(),end)
			for line in self.trace_in_mem :
				actual_ts=float(line.split(',')[1])/1000.0;
				if ( ((actual_ts-self.start_time) >= 0 ) and 
				     ((actual_ts-self.start_time) <= epoch_end - epoch_start  )) :
					mod_ts=actual_ts-self.start_time+epoch_start;
					records=line.split(',')
					new_line=records[0]+","+str(mod_ts);
					for i in range (2,len(records)) :
						new_line+=","+records[i]
					fh.write(new_line)
			time_written_out=epoch_end
