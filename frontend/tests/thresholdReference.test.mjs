import test from 'node:test';
import assert from 'node:assert/strict';
import {thresholdCoefficient} from '../src/thresholdReference.ts';

test('coefficient uses saved settings or explicit legacy CSV input, never rounded watts',()=>{
 assert.equal(thresholdCoefficient({settings:{threshold_coefficient:.8}}),.8);
 assert.equal(thresholdCoefficient({settings:{},historical_fields:{coeff_soglia:'0,8'}}),.8);
 assert.equal(thresholdCoefficient({analysis:{map_w:176,threshold_w:141}}),null);
 assert.equal(thresholdCoefficient({settings:{threshold_coefficient:.75},historical_fields:{coeff_soglia:'.8'}}),.75);
 assert.equal(thresholdCoefficient({settings:{threshold_coefficient:null},historical_fields:{coeff_soglia:'.8'}}),null);
 for(const value of ['', 'NaN','Infinity',0,-1,3])assert.equal(thresholdCoefficient({historical_fields:{coeff_soglia:value}}),null);
});
