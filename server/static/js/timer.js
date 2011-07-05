/*
 * Timer similiar to java
 *
 * Written in Classy
 * @author: Nijikokun<nijikokun@gmail.com>
 * @copyright: Nijikokun 2011
 */

var Timer = Class.$extend({
    Settings: {
      timer: null,
      running: false,
      runOnce: false,
      canRun: [],
      interval: 500,
      callbacks: [],
      multipliers: [],
      ticks: [],
      completed: 0,
      paused: -1,
      started: -1
    },
    
    __init__: function( interval, callback ) {
        this.Settings.interval = parseInt(interval);
        this.addCallback(callback);
        
        return this;
    },
    
    runnable: function ( bool ) {
        if(typeof bool == "boolean") this.Settings.runOnce = bool;
        
        return this;
    },
    
    interval: function ( interval ) {
        if (typeof interval == 'number') this.Settings.interval = Math.floor(interval);
        
        return this;
    },
    
    addCallback: function( obj, n ) {
        if (typeof obj == "function") {
            this.Settings.callbacks.push(obj);
            
            if (typeof n == "number") {
                n = Math.floor(n);
                this.Settings.multipliers.push((n < 1 ? 1 : n));
            } else this.Settings.multipliers.push(1);
            
            this.Settings.ticks.push(0);
            this.Settings.canRun.push(true);
        }
        
        return this;
    },
    
    pulse: function( interval ) {
        var me = this;
        for (var i = 0; i < this.Settings.callbacks.length; i++) {
            if (typeof this.Settings.callbacks[i] == "function" && this.Settings.canRun[i]) {
                this.Settings.ticks[i]++;
                
                if (this.Settings.ticks[i] == this.Settings.multipliers[i]) {
                    this.Settings.ticks[i] = 0;
                    
                    if (this.Settings.runOnce) {
                        this.Settings.canRun[i] = false;
                        this.Settings.completed++;
                    }
                    
                    window.setTimeout(me.Settings.callbacks[i], 0);
                }
            }
        }
        
        if (this.Settings.runOnce && this.Settings.completed == this.Settings.callbacks.length) this.stop();
        if (typeof interval == "number") this.stop().start(null, true);
    },
    
    reset: function () {
        this.Settings.completed = 0;
        this.Settings.started = -1;
        this.Settings.paused = -1;
        
        for (var i = 0; i < this.Settings.callbacks.length; i++) {
            this.Settings.canRun[i] = true;
            this.Settings.ticks[i] = 0;
        }
    },
    
    start: function( init, noRestart ) {
        if (this.paused()) return this.resume();
        if (!this.stopped()) return this;
        if (!noRestart) this.reset();
        
        var temporal = this.Settings.interval;
        if (typeof init == 'number') temporal = init;
        
        var me = this;
        this.Settings.timer = window.setInterval(function () { me.pulse(init); }, temporal);
        this.Settings.started = (new Date()).getTime();
        this.Settings.started -= (this.Settings.interval - temporal);
        
        return this;
    },
    
    restart: function () {
        return this.stop().start();
    },
    
    pause: function () {
        if (this.Settings.timer) {
            this.Settings.paused = (new Date()).getTime();
            this.stop(true);
        }
        
        return this;
    },
    
    stop: function ( pause ) {
        if (this.Settings.timer) {
            if (!pause) this.Settings.paused = -1;
            try { window.clearInterval(this.Settings.timer); } catch (ex) { }
            this.Settings.timer = null;
        }
        
        return this;
    },
    
    stopped: function () {
        return ((this.Settings.timer == null) && !this.paused());
    },
    
    paused: function () {
        return (this.Settings.paused >= 0);
    },
    
    clear: function () {
        this.Settings.callbacks.length = 0;
        this.Settings.multipliers.length = 0;
        this.Settings.canRun.length = 0;
        this.Settings.ticks.length = 0;
        this.Settings.completed = 0;
        
        return this;
    }
});