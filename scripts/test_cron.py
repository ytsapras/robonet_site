# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 21:57:57 2016

@author: robouser
"""
import k2_footprint_class

def test_cron():
    
    fileobj = open('/home/robouser/cron_test.dat','w')
    t = datetime.utcnow()
    fileobj.write( t.strftime("%Y-%m-%dT%H:%M:%S") + '\n' )
    fileobj.write('Completed imports\n')
    fileobj.flush()
    
    k2_campaign = k2_footprint_class.K2Footprint( 9, 2016 )
    
    fileobj.write('Loaded K2 Campaign data')   
    fileobj.flush() 
    
    fileobj.close()
    
if __name__ == '__main__':
    test_cron()