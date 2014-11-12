/*
 * Copyright 2012-2014 Narantech Inc. All rights reserved.
 *  __    _ _______ ______   _______ __    _ _______ _______ _______ __   __
 * |  |  | |   _   |    _ | |   _   |  |  | |       |       |       |  | |  |
 * |   |_| |  |_|  |   | || |  |_|  |   |_| |_     _|    ___|       |  |_|  |
 * |       |       |   |_||_|       |       | |   | |   |___|       |       |
 * |  _    |       |    __  |       |  _    | |   | |    ___|      _|       |
 * | | |   |   _   |   |  | |   _   | | |   | |   | |   |___|     |_|   _   |
 * |_|  |__|__| |__|___|  |_|__| |__|_|  |__| |___| |_______|_______|__| |__|
 *
 * ApiWeb library client.
 */
;(function($) {
  "use strict";
  $.ApiWeb= function(path) {
    var base = this, o;
    var ws_protocol = window.location.protocol == 'https:' ? 'wss:' : 'ws:';
    var conn = new WebSocket(ws_protocol + '//' + window.location.host + '/' + path);

    // reserved functions for ApiWeb
    var reserved = { 'on': '', 'reload': '', 'ready': '', 'close': '' };

    var handlers = {};  // event id -> function
    base.ready = false;
    base.close = function() {
      console.log("Closing the connection. path=" + path);
      conn.close();
    };
    // Event handlers
    base.on = function(ident, handler) {
      var cbs = handlers[ident];
      if (!cbs) {
        cbs = $.Callbacks();
        handlers[ident] = cbs;
      }
      if (handler) {
        cbs.add(handler);
      }
    };
    // Default events
    base.on('ready', null);
    base.on('close', null);

    conn.onclose = function (e) {
      handlers['close'].fire(base);
    };

    var requests = {};  // request db : ident -> callback
    // Reply handler
    var handle_reply = function(ident, data) {
        if (ident in requests) {
          var callback = requests[ident];
          delete requests[ident];
          callback(data);
        } else {
          console.log("Info: Handler " + ident + " not registered.");
        }
      };

    // Requests
    var send_request = function(name, args) {
      var req = {};
      req['ident'] = Math.random().toString(36).substr(2, 5);
      req['value'] = { 'name': name, 'args': args };
      conn.send(JSON.stringify(req));
      return function(callback) {
        requests[req.ident] = callback;
      };
    };

    // Server events
    conn.onmessage = function(e) {
      var data = JSON.parse(e.data);
      if (data.op == 'init') {
        console.log("Init ApiWeb : " + data);
        $.each(data.value, function(i, name) {
          if (!(name in reserved)) {
            console.log("Loaded API : " + name);
            base[name] = function() {
              return send_request(name, Array.prototype.slice.call(arguments));
            };
          } else {
            console.log("Warning: " + name + " is a reserved function.");
          }
        });
        base.ready = true;
        handlers['ready'].fire(base);
      } else if (data.op == 'reply') {
        handle_reply(data.ident, data.value);
      } else if (data.op == 'event') {
        var handler = handlers[data.ident];
        if (handler) {
          handler.fire(base, data.value);
        } else {
          console.log("Info: the event has no handlers. " + data.ident);
        }
      } else {
        // unknown message
        console.log("Unknown server message: " + e.data);
      }
    };
  }
})(jQuery);

