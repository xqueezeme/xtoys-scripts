function funscript_alternatePattern(actions, patternGenerationRate) {
    var length = actions.slice(-1).pop().at;
    var normalSamples = length / patternGenerationRate;
    var fadeTime = 3000;
    var fadeSamples = fadeTime / patternGenerationRate;
  
    var totalSamples = normalSamples + (fadeSamples * 2);
    var sample = 0;
    var actionIndex = 0;
  
    var a1 = actions[0];
    var a0 = a1;
    var left = [];
    var right = [];
    sample = a0.at / patternGenerationRate;
      while(sample < totalSamples) {
            var ms = sample * patternGenerationRate;
  
        if(a1.at < ms && actionIndex < actions.length - 1) {
          a0 = a1;
          actionIndex++;
          a1 = actions[actionIndex];
        }
        
        var dist = a1.at - a0.at;
        var distFromNow = a1.at - ms;
        
        var dpos = a1.pos - a0.pos;
        var alpha = Math.max(0, Math.min(1, (ms - a0.at) / dist)) || 0;
        var pos = Math.floor(a0.pos + dpos * alpha);
        var fade = 1;
        if(dist > fadeTime * 2) {
            if(distFromNow < fadeTime) {
                 fade = Math.max(0, 1 - (distFromNow / fadeTime));
            } else if(dist - distFromNow > fadeTime) {
                fade = Math.max(0, 1 - ((dist - distFromNow - fadeTime)/fadeTime));
            }
        }
        left.push({'pos': Math.floor((100-pos) * fade), 'at': ms});
        right.push({'pos': Math.floor(pos * fade), 'at': ms});
  
        if(fade == 0) {
            if(distFromNow - fadeTime > 0) {
                var newSample = (a1.at - fadeTime) / patternGenerationRate;
                if(newSample <= sample) {
                    sample++;
                } else {
                    sample = newSample;
                }
            } else {
              sample++;
            }
        } else {
          sample++;
        }
      }
    return { 'a': left, 'b': right};
  }
  
  
  function funscript_normalizePattern(actions, min, max, targetMin, targetMax) {
      if(actions) {
          targetMin = targetMin > 0 ? parseInt(targetMin) : 0;
          targetMax = targetMax > 0 && targetMax < 100 ? parseInt(targetMax) : 100;
  
          for(i = 0; i<actions.length; i++) {
              var pos = parseInt(actions[i].pos);
              var percent = (parseInt(pos) - parseInt(min)) / parseInt(max);
              var newPos = Math.floor(((targetMax - targetMin) * percent) + targetMin);
              actions[i].pos = newPos;
          }
      }
      return actions;
  }
  
  function funscript_smoothPattern(
      actions, 
      patternGenerationRate, 
      patternGenerationTickMaxChange
      ) {
      var length = actions.slice(-1).pop().at;
      var target = 0;
      var normalSamples = length / patternGenerationRate;
      var totalSamples = normalSamples;
      var current = 0;
      var actionIndex = 0;
      var previousPosition = 0;
      var position = 0;
      var newActions = [];
  
      max = 0;
      min = null;
      var a1 = actions[0];
      var a0 = a1;
      var sample = (a0.at / patternGenerationRate) - (100 / patternGenerationTickMaxChange);
  
      while(sample < totalSamples) {
          var ms = sample * patternGenerationRate;
          if(a1.at < ms && actionIndex < actions.length - 1) {
              var old = a1;
              var positions = 0;
              previousPosition = position;
              while(a1.at < ms && actionIndex < actions.length - 1) {
                  a0 = a1;
                  actionIndex++;
                  a1 = actions[actionIndex];
                  positions += a1.pos * (a1.at - a0.at);
              }
              position = Math.floor(positions/(a1.at - old.at));
          }
          var distFromNow = a1.at - ms;
          var dpos = position - previousPosition;
          var steps = Math.ceil(Math.abs(dpos) / patternGenerationTickMaxChange);
          var samplesLeft = Math.floor(distFromNow / patternGenerationRate);
  
          if(steps >= samplesLeft) {
              target = position;
              if(current != target) {
                  if(current < target) {
                      current += Math.min(target - current, patternGenerationTickMaxChange);
                  } else {
                      current -= Math.min(current - target, patternGenerationTickMaxChange);
                  }
                  current = Math.min(100, Math.max(0, current));
                  if(max < current) {
                      max = current;
                  }
                  if(min == null || min > current) {
                      min = current;
                  }
                  newActions.push({ 'at': ms, 'pos': current});
              }
              sample++;
          } else {
              var increase = (samplesLeft - steps + 1) > 1 ? samplesLeft - steps + 1 : 1;
              sample += Math.floor(increase);
          }
      }
      return { 'min': min, 'max': max, 'actions': newActions};
  }