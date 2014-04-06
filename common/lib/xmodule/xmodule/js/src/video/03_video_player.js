(function (requirejs, require, define) {

// VideoPlayer module.
define(
'video/03_video_player.js',
['video/02_html5_video.js', 'video/00_resizer.js'],
function (HTML5Video, Resizer) {
    var dfd = $.Deferred(),
        VideoPlayer = function (state) {
            state.videoPlayer = {};
            _makeFunctionsPublic(state);
            _initialize(state);
            // No callbacks to DOM events (click, mousemove, etc.).

            return dfd.promise();
        },
        methodsDict = {
            duration: duration,
            handlePlaybackQualityChange: handlePlaybackQualityChange,
            isEnded: isEnded,
            isPlaying: isPlaying,
            log: log,
            onCaptionSeek: onSeek,
            onEnded: onEnded,
            onPause: onPause,
            onPlay: onPlay,
            onPlaybackQualityChange: onPlaybackQualityChange,
            onReady: onReady,
            onSlideSeek: onSeek,
            onSpeedChange: onSpeedChange,
            onStateChange: onStateChange,
            onUnstarted: onUnstarted,
            onVolumeChange: onVolumeChange,
            pause: pause,
            play: play,
            setPlaybackRate: setPlaybackRate,
            update: update,
            figureOutStartEndTime: figureOutStartEndTime,
            figureOutStartingTime: figureOutStartingTime,
            updatePlayTime: updatePlayTime
        };

    VideoPlayer.prototype = methodsDict;

    // VideoPlayer() function - what this module "exports".
    return VideoPlayer;

    // ***************************************************************
    // Private functions start here.
    // ***************************************************************

    // function _makeFunctionsPublic(state)
    //
    //     Functions which will be accessible via 'state' object. When called,
    //     these functions will get the 'state' object as a context.
    function _makeFunctionsPublic(state) {
        state.bindTo(methodsDict, state.videoPlayer, state);
    }

    // function _initialize(state)
    //
    //     Create any necessary DOM elements, attach them, and set their
    //     initial configuration. Also make the created DOM elements available
    //     via the 'state' object. Much easier to work this way - you don't
    //     have to do repeated jQuery element selects.
    function _initialize(state) {
        var youTubeId, player;

        // The function is called just once to apply pre-defined configurations
        // by student before video starts playing. Waits until the video's
        // metadata is loaded, which normally happens just after the video
        // starts playing. Just after that configurations can be applied.
        state.videoPlayer.ready = _.once(function () {
            $(window).on('unload', state.saveState);

            if (!state.isFlashMode()) {
                state.videoPlayer.setPlaybackRate(state.speed);
            }
            state.videoPlayer.player.setVolume(state.currentVolume);
        });

        if (state.videoType === 'youtube') {
            state.videoPlayer.PlayerState = YT.PlayerState;
            state.videoPlayer.PlayerState.UNSTARTED = -1;
        } else { // if (state.videoType === 'html5') {
            state.videoPlayer.PlayerState = HTML5Video.PlayerState;
        }

        state.videoPlayer.currentTime = 0;

        state.videoPlayer.goToStartTime = true;
        state.videoPlayer.stopAtEndTime = true;

        state.videoPlayer.playerVars = {
            controls: 0,
            wmode: 'transparent',
            rel: 0,
            showinfo: 0,
            enablejsapi: 1,
            modestbranding: 1
        };

        if (!state.isFlashMode()) {
            state.videoPlayer.playerVars.html5 = 1;
        }

        // There is a bug which prevents YouTube API to correctly set the speed
        // to 1.0 from another speed in Firefox when in HTML5 mode. There is a
        // fix which basically reloads the video at speed 1.0 when this change
        // is requested (instead of simply requesting a speed change to 1.0).
        // This has to be done only when the video is being watched in Firefox.
        // We need to figure out what browser is currently executing this code.
        //
        // TODO: Check the status of
        // http://code.google.com/p/gdata-issues/issues/detail?id=4654
        // When the YouTube team fixes the API bug, we can remove this
        // temporary bug fix.
        state.browserIsFirefox = navigator.userAgent
            .toLowerCase().indexOf('firefox') > -1;

        if (state.videoType === 'html5') {
            state.videoPlayer.player = new HTML5Video.Player(state.el, {
                playerVars:   state.videoPlayer.playerVars,
                videoSources: state.html5Sources,
                events: {
                    onReady:       state.videoPlayer.onReady,
                    onStateChange: state.videoPlayer.onStateChange
                }
            });

            player = state.videoEl = state.videoPlayer.player.videoEl;

            player[0].addEventListener('loadedmetadata', function () {
                var videoWidth = player[0].videoWidth || player.width(),
                    videoHeight = player[0].videoHeight || player.height();

                _resize(state, videoWidth, videoHeight);

                _updateVcrAndRegion(state);
            }, false);

        } else { // if (state.videoType === 'youtube') {
            youTubeId = state.youtubeId();

            state.videoPlayer.player = new YT.Player(state.id, {
                playerVars: state.videoPlayer.playerVars,
                videoId: youTubeId,
                events: {
                    onReady: state.videoPlayer.onReady,
                    onStateChange: state.videoPlayer.onStateChange,
                    onPlaybackQualityChange: state.videoPlayer
                        .onPlaybackQualityChange
                }
            });

            state.el.on('initialize', function () {
                var player = state.videoEl = state.el.find('iframe'),
                    videoWidth = player.attr('width') || player.width(),
                    videoHeight = player.attr('height') || player.height();

                _resize(state, videoWidth, videoHeight);
                _updateVcrAndRegion(state, true);
            });
        }

        if (state.isTouch) {
            dfd.resolve();
        }
    }

    function _updateVcrAndRegion(state, isYoutube) {
        var update = function (state) {
            var duration = state.videoPlayer.duration(),
                time;

            time = state.videoPlayer.figureOutStartingTime(duration);

            // Update the VCR.
            state.trigger(
                'videoControl.updateVcrVidTime',
                {
                    time: time,
                    duration: duration
                }
            );

            // Update the time slider.
            state.trigger(
                'videoProgressSlider.updateStartEndTimeRegion',
                {
                    duration: duration
                }
            );
            state.trigger(
                'videoProgressSlider.updatePlayTime',
                {
                    time: time,
                    duration: duration
                }
            );
        };

        // After initialization, update the VCR with total time.
        // At this point only the metadata duration is available (not
        // very precise), but it is better than having 00:00:00 for
        // total time.
        if (state.youtubeMetadataReceived || !isYoutube) {
            // Metadata was already received, and is available.
            update(state);
        } else {
            // We wait for metadata to arrive, before we request the update
            // of the VCR video time, and of the start-end time region.
            // Metadata contains duration of the video.
            state.el.on('metadata_received', function () {
                update(state);
            });
        }
    }

    function _resize(state, videoWidth, videoHeight) {
        state.resizer = new Resizer({
                element: state.videoEl,
                elementRatio: videoWidth/videoHeight,
                container: state.container
            })
            .callbacks.once(function() {
                state.el.trigger('caption:resize');
            })
            .setMode('width');

        // Update captions size when controls becomes visible on iPad or Android
        if (/iPad|Android/i.test(state.isTouch[0])) {
            state.el.on('controls:show', function () {
                state.el.trigger('caption:resize');
            });
        }

        $(window).on('resize', _.debounce(function () {
            state.trigger('videoControl.updateControlsHeight', null);
            state.el.trigger('caption:resize');
            state.resizer.align();
        }, 100));
    }

    // function _restartUsingFlash(state)
    //
    //     When we are about to play a YouTube video in HTML5 mode and discover
    //     that we only have one available playback rate, we will switch to
    //     Flash mode. In Flash speed switching is done by reloading videos
    //     recorded at different frame rates.
    function _restartUsingFlash(state) {
        // Remove from the page current iFrame with HTML5 video.
        state.videoPlayer.player.destroy();

        state.setPlayerMode('flash');

        console.log('[Video info]: Changing YouTube player mode to "flash".');

        // Removed configuration option that requests the HTML5 mode.
        delete state.videoPlayer.playerVars.html5;

        // Request for the creation of a new Flash player
        state.videoPlayer.player = new YT.Player(state.id, {
            playerVars: state.videoPlayer.playerVars,
            videoId: state.youtubeId(),
            events: {
                onReady: state.videoPlayer.onReady,
                onStateChange: state.videoPlayer.onStateChange,
                onPlaybackQualityChange: state.videoPlayer
                    .onPlaybackQualityChange
            }
        });

        _updateVcrAndRegion(state, true);
        state.el.trigger('caption:fetch');
        state.resizer.setElement(state.el.find('iframe')).align();
    }

    // ***************************************************************
    // Public functions start here.
    // These are available via the 'state' object. Their context ('this'
    // keyword) is the 'state' object. The magic private function that makes
    // them available and sets up their context is makeFunctionsPublic().
    // ***************************************************************

    function pause() {
        if (this.videoPlayer.player.pauseVideo) {
            this.videoPlayer.player.pauseVideo();
        }
    }

    function play() {
        if (this.videoPlayer.player.playVideo) {
            if (this.videoPlayer.isEnded()) {
                // When the video will start playing again from the start, the
                // start-time and end-time will come back into effect.
                this.videoPlayer.goToStartTime = true;
                this.videoPlayer.stopAtEndTime = true;
            }

            this.videoPlayer.player.playVideo();
        }
    }

    // This function gets the video's current play position in time
    // (currentTime) and its duration.
    // It is called at a regular interval when the video is playing.
    function update() {
        this.videoPlayer.currentTime = this.videoPlayer.player.getCurrentTime();

        if (isFinite(this.videoPlayer.currentTime)) {
            this.videoPlayer.updatePlayTime(this.videoPlayer.currentTime);

            // We need to pause the video if current time is smaller (or equal)
            // than end-time. Also, we must make sure that this is only done
            // once per video playing from start to end.
            if (
                this.videoPlayer.stopAtEndTime &&
                this.videoPlayer.endTime !== null &&
                this.videoPlayer.endTime <= this.videoPlayer.currentTime
            ) {
                this.videoPlayer.stopAtEndTime = false;

                this.videoPlayer.pause();

                this.trigger('videoProgressSlider.notifyThroughHandleEnd', {
                    end: true
                });
            }
        }
    }

    function setPlaybackRate(newSpeed) {
        var time = this.videoPlayer.currentTime,
            methodName, youtubeId;

        if (
            this.isHtml5Mode() &&
            !(
                this.browserIsFirefox &&
                newSpeed === '1.0' &&
                this.videoType === 'youtube'
            )
        ) {
            this.videoPlayer.player.setPlaybackRate(newSpeed);
        } else {
            // We request the reloading of the video in the case when YouTube
            // is in Flash player mode, or when we are in Firefox, and the new
            // speed is 1.0. The second case is necessary to avoid the bug
            // where in Firefox speed switching to 1.0 in HTML5 player mode is
            // handled incorrectly by YouTube API.
            methodName = 'cueVideoById';
            youtubeId = this.youtubeId(newSpeed);

            if (this.videoPlayer.isPlaying()) {
                methodName = 'loadVideoById';
            }

            this.videoPlayer.player[methodName](youtubeId, time);
            this.videoPlayer.updatePlayTime(time);
        }
    }

    function onSpeedChange(newSpeed) {
        var time = this.videoPlayer.currentTime;

        if (this.isFlashMode()) {
            this.videoPlayer.currentTime = Time.convert(
                time,
                parseFloat(this.speed),
                newSpeed
            );
        }

        newSpeed = parseFloat(newSpeed).toFixed(2).replace(/\.00$/, '.0');

        this.videoPlayer.log(
            'speed_change_video',
            {
                current_time: time,
                old_speed: this.speed,
                new_speed: newSpeed
            }
        );

        this.setSpeed(newSpeed, true);
        this.videoPlayer.setPlaybackRate(newSpeed);
        this.saveState(true, { speed: newSpeed });
    }

    // Every 200 ms, if the video is playing, we call the function update, via
    // clearInterval. This interval is called updateInterval.
    // It is created on a onPlay event. Cleared on a onPause event.
    // Reinitialized on a onSeek event.
    function onSeek(params) {
        var duration = this.videoPlayer.duration(),
            newTime = params.time;

        if (
            (typeof newTime !== 'number') ||
            (newTime > duration) ||
            (newTime < 0)
        ) {
            return;
        }

        this.videoPlayer.log(
            'seek_video',
            {
                old_time: this.videoPlayer.currentTime,
                new_time: newTime,
                type: params.type
            }
        );

        // After the user seeks, the video will start playing from
        // the sought point, and stop playing at the end.
        this.videoPlayer.goToStartTime = false;
        if (newTime > this.videoPlayer.endTime || this.videoPlayer.endTime === null) {
            this.videoPlayer.stopAtEndTime = false;
        }

        this.videoPlayer.player.seekTo(newTime, true);

        if (this.videoPlayer.isPlaying()) {
            clearInterval(this.videoPlayer.updateInterval);
            this.videoPlayer.updateInterval = setInterval(
                this.videoPlayer.update, 200
            );

            setTimeout(this.videoPlayer.update, 0);
        } else {
            this.videoPlayer.currentTime = newTime;
        }

        this.videoPlayer.updatePlayTime(newTime);

        this.el.trigger('seek', arguments);
    }

    function onEnded() {
        var time = this.videoPlayer.duration();

        this.trigger('videoControl.pause', null);
        this.trigger('videoProgressSlider.notifyThroughHandleEnd', {
            end: true
        });

        if (this.videoPlayer.skipOnEndedStartEndReset) {
            this.videoPlayer.skipOnEndedStartEndReset = undefined;
        }

        // Sometimes `onEnded` events fires when `currentTime` not equal
        // `duration`. In this case, slider doesn't reach the end point of
        // timeline.
        this.videoPlayer.updatePlayTime(time);

        this.el.trigger('ended', arguments);
    }

    function onPause() {
        this.videoPlayer.log(
            'pause_video',
            {
                currentTime: this.videoPlayer.currentTime
            }
        );

        clearInterval(this.videoPlayer.updateInterval);
        delete this.videoPlayer.updateInterval;

        this.trigger('videoControl.pause', null);
        this.saveState(true);
        this.el.trigger('pause', arguments);
    }

    function onPlay() {
        this.videoPlayer.log(
            'play_video',
            {
                currentTime: this.videoPlayer.currentTime
            }
        );

        if (!this.videoPlayer.updateInterval) {
            this.videoPlayer.updateInterval = setInterval(
                this.videoPlayer.update, 200
            );

            this.videoPlayer.update();
        }

        this.trigger('videoControl.play', null);
        this.trigger('videoProgressSlider.notifyThroughHandleEnd', {
            end: false
        });
        this.videoPlayer.ready();
        this.el.trigger('play', arguments);
    }

    function onUnstarted() { }

    function handlePlaybackQualityChange(value) {
        this.videoPlayer.player.setPlaybackQuality(value);
    }

    function onPlaybackQualityChange() {
        var quality;

        quality = this.videoPlayer.player.getPlaybackQuality();

        this.trigger('videoQualityControl.onQualityChange', quality);

        this.el.trigger('qualitychange', arguments);
    }

    function onReady() {
        var _this = this,
            availablePlaybackRates, baseSpeedSubs,
            player, videoWidth, videoHeight;

        dfd.resolve();

        this.el.on('speedchange', function (event, speed) {
            _this.videoPlayer.onSpeedChange(speed);
        });

        this.videoPlayer.log('load_video');

        availablePlaybackRates = this.videoPlayer.player
                                    .getAvailablePlaybackRates();

        // Because of problems with muting sound outside of range 0.25 and
        // 5.0, we should filter our available playback rates.
        // Issues:
        //   https://code.google.com/p/chromium/issues/detail?id=264341
        //   https://bugzilla.mozilla.org/show_bug.cgi?id=840745
        //   https://developer.mozilla.org/en-US/docs/DOM/HTMLMediaElement

        availablePlaybackRates = _.filter(
            availablePlaybackRates,
            function (item) {
                var speed = Number(item);
                return speed > 0.25 && speed <= 5;
            }
        );

        // Because of a recent change in the YouTube API (not documented), sometimes
        // HTML5 mode loads after Flash mode has been loaded. In this case we have
        // multiple speeds available but the variable `this.currentPlayerMode` is
        // set to "flash". This is impossible because in Flash mode we can have
        // only one speed available. Therefore we must execute the following code
        // block if we have multiple speeds or if `this.currentPlayerMode` is set to
        // "html5". If any of the two conditions are true, we then set the variable
        // `this.currentPlayerMode` to "html5".
        //
        // For more information, please see the PR that introduced this change:
        //     https://github.com/edx/edx-platform/pull/2841
        if (
            (this.isHtml5Mode() || availablePlaybackRates.length > 1) &&
            this.videoType === 'youtube'
        ) {
            if (availablePlaybackRates.length === 1 && !this.isTouch) {
                // This condition is needed in cases when Firefox version is
                // less than 20. In those versions HTML5 playback could only
                // happen at 1 speed (no speed changing). Therefore, in this
                // case, we need to switch back to Flash.
                //
                // This might also happen in other browsers, therefore when we
                // have 1 speed available, we fall back to Flash.

                _restartUsingFlash(this);
            } else if (availablePlaybackRates.length > 1) {
                this.setPlayerMode('html5');

                // We need to synchronize available frame rates with the ones
                // that the user specified.

                baseSpeedSubs = this.videos['1.0'];
                // this.videos is a dictionary containing various frame rates
                // and their associated subs.

                // First clear the dictionary.
                $.each(this.videos, function (index, value) {
                    delete _this.videos[index];
                });
                this.speeds = [];
                // Recreate it with the supplied frame rates.
                $.each(availablePlaybackRates, function (index, value) {
                    var key = value.toFixed(2).replace(/\.00$/, '.0');

                    _this.videos[key] = baseSpeedSubs;
                    _this.speeds.push(key);
                });

                this.setSpeed(this.speed);
                this.el.trigger('speed:render', [this.speeds, this.speed]);
            }
        }

        if (this.isFlashMode()) {
            this.setSpeed(this.speed);
            this.el.trigger('speed:set', [this.speed]);
        }

        if (this.isHtml5Mode()) {
            this.videoPlayer.player.setPlaybackRate(this.speed);
        }

        this.el.trigger('ready', arguments);
        /* The following has been commented out to make sure autoplay is
           disabled for students.
        if (
            !this.isTouch &&
            $('.video:first').data('autoplay') === 'True'
        ) {
            this.videoPlayer.play();
        }
        */
    }

    function onStateChange(event) {
        switch (event.data) {
            case this.videoPlayer.PlayerState.UNSTARTED:
                this.videoPlayer.onUnstarted();
                break;
            case this.videoPlayer.PlayerState.PLAYING:
                this.videoPlayer.onPlay();
                break;
            case this.videoPlayer.PlayerState.PAUSED:
                this.videoPlayer.onPause();
                break;
            case this.videoPlayer.PlayerState.ENDED:
                this.videoPlayer.onEnded();
                break;
            case this.videoPlayer.PlayerState.CUED:
                this.videoPlayer.player.seekTo(this.videoPlayer.seekToTimeOnCued, true);
                // We need to call play() explicitly because after the call
                // to functions cueVideoById() followed by seekTo() the video
                // is in a PAUSED state.
                //
                // Why? This is how the YouTube API is implemented.
                this.videoPlayer.play();
                break;
        }
    }

    function figureOutStartEndTime(duration) {
        var videoPlayer = this.videoPlayer;

        videoPlayer.startTime = this.config.startTime;
        if (videoPlayer.startTime >= duration) {
            videoPlayer.startTime = 0;
        } else if (this.isFlashMode()) {
            videoPlayer.startTime /= Number(this.speed);
        }

        videoPlayer.endTime = this.config.endTime;
        if (
            videoPlayer.endTime <= videoPlayer.startTime ||
            videoPlayer.endTime >= duration
        ) {
            videoPlayer.stopAtEndTime = false;
            videoPlayer.endTime = null;
        } else if (this.isFlashMode()) {
            videoPlayer.endTime /= Number(this.speed);
        }
    }

    function figureOutStartingTime(duration) {
        var savedVideoPosition = this.config.savedVideoPosition,

            // Default starting time is 0. This is the case when
            // there is not start-time, no previously saved position,
            // or one (or both) of those values is incorrect.
            time = 0,

            startTime, endTime;

        this.videoPlayer.figureOutStartEndTime(duration);

        startTime = this.videoPlayer.startTime;
        endTime   = this.videoPlayer.endTime;

        if (startTime > 0) {
            if (
                startTime < savedVideoPosition &&
                (endTime > savedVideoPosition || endTime === null) &&

                // We do not want to jump to the end of the video.
                // We subtract 1 from the duration for a 1 second
                // safety net.
                savedVideoPosition < duration - 1
            ) {
                time = savedVideoPosition;
            } else {
                time = startTime;
            }
        } else if (
            savedVideoPosition > 0 &&
            (endTime > savedVideoPosition || endTime === null) &&

            // We do not want to jump to the end of the video.
            // We subtract 1 from the duration for a 1 second
            // safety net.
            savedVideoPosition < duration - 1
        ) {
            time = savedVideoPosition;
        }

        return time;
    }

    function updatePlayTime(time) {
        var videoPlayer = this.videoPlayer,
            duration = this.videoPlayer.duration(),
            youTubeId;

        if (duration > 0 && videoPlayer.goToStartTime) {
            videoPlayer.goToStartTime = false;

            // The duration might have changed. Update the start-end time region to
            // reflect this fact.
            this.trigger(
                'videoProgressSlider.updateStartEndTimeRegion',
                {
                    duration: duration
                }
            );

            time = videoPlayer.figureOutStartingTime(duration);

            // When the video finishes playing, we will start from the
            // start-time, or from the beginning (rather than from the remembered
            // position).
            this.config.savedVideoPosition = 0;

            if (time > 0) {
                // After a bug came up (BLD-708: "In Firefox YouTube video with
                // start-time plays from 00:00:00") the video refused to play
                // from start-time, and only played from the beginning.
                //
                // It turned out that for some reason if Firefox you couldn't
                // seek beyond some amount of time before the video loaded.
                // Very strange, but in Chrome there is no such bug.
                //
                // HTML5 video sources play fine from start-time in both Chrome
                // and Firefox.
                if (this.browserIsFirefox && this.videoType === 'youtube') {
                    youTubeId = this.youtubeId();

                    // When we will call cueVideoById() for some strange reason
                    // an ENDED event will be fired. It really does no damage
                    // except for the fact that the end-time is reset to null.
                    // We do not want this.
                    //
                    // The flag `skipOnEndedStartEndReset` will notify the
                    // onEnded() callback for the ENDED event that there
                    // is no need in resetting the start-time and end-time.
                    videoPlayer.skipOnEndedStartEndReset = true;

                    videoPlayer.seekToTimeOnCued = time;
                    videoPlayer.player.cueVideoById(youTubeId, time);
                } else {
                    videoPlayer.player.seekTo(time);
                }
            }
        }

        this.trigger(
            'videoProgressSlider.updatePlayTime',
            {
                time: time,
                duration: duration
            }
        );

        this.trigger(
            'videoControl.updateVcrVidTime',
            {
                time: time,
                duration: duration
            }
        );

        this.el.trigger('caption:update', [time]);
    }

    function isEnded() {
        var playerState = this.videoPlayer.player.getPlayerState(),
            ENDED = this.videoPlayer.PlayerState.ENDED;

        return playerState === ENDED;
    }

    function isPlaying() {
        var playerState = this.videoPlayer.player.getPlayerState(),
            PLAYING = this.videoPlayer.PlayerState.PLAYING;

        return playerState === PLAYING;
    }

    /*
     * Return the duration of the video in seconds.
     *
     * First, try to use the native player API call to get the duration.
     * If the value returned by the native function is not valid, resort to
     * the value stored in the metadata for the video. Note that the metadata
     * is available only for YouTube videos.
     *
     * IMPORTANT! It has been observed that sometimes, after initial playback
     * of the video, when operations "pause" and "play" are performed (in that
     * sequence), the function will start returning a slightly different value.
     *
     * For example: While playing for the first time, the function returns 31.
     * After pausing the video and then resuming once more, the function will
     * start returning 31.950656.
     *
     * This instability is internal to the player API (or browser internals).
     */
    function duration() {
        var dur;

        // Sometimes the YouTube API doesn't finish instantiating all of it's
        // methods, but the execution point arrives here.
        //
        // This happens when you have start-time and end-time set, and click "Edit"
        // in Studio, and then "Save". The Video editor dialog closes, the
        // video reloads, but the start-end range is not visible.
        if (this.videoPlayer.player.getDuration) {
            dur = this.videoPlayer.player.getDuration();
        }

        // For YouTube videos, before the video starts playing, the API
        // function player.getDuration() will return 0. This means that the VCR
        // will show total time as 0 when the page just loads (before the user
        // clicks the Play button).
        //
        // We can do betterin a case when dur is 0 (or less than 0). We can ask
        // the getDuration() function for total time, which will query the
        // metadata for a duration.
        //
        // Be careful! Often the metadata duration is not very precise. It
        // might differ by one or two seconds against the actual time as will
        // be reported later on by the player.getDuration() API function.
        if (!isFinite(dur) || dur <= 0) {
            if (this.videoType === 'youtube') {
                dur = this.getDuration();
            }
        }

        // Just in case the metadata is garbled, or something went wrong, we
        // have a final check.
        if (!isFinite(dur) || dur <= 0) {
            dur = 0;
        }

        return Math.floor(dur);
    }

    function log(eventName, data) {
        var logInfo;

        // Default parameters that always get logged.
        logInfo = {
            id:   this.id
        };

        // If extra parameters were passed to the log.
        if (data) {
            $.each(data, function (paramName, value) {
                logInfo[paramName] = value;
            });
        }

        if (this.videoType === 'youtube') {
            logInfo.code = this.youtubeId();
        } else  if (this.videoType === 'html5') {
            logInfo.code = 'html5';
        }

        Logger.log(eventName, logInfo);
    }

    function onVolumeChange(volume) {
        this.videoPlayer.player.setVolume(volume);
        this.el.trigger('volumechange', arguments);
    }
});

}(RequireJS.requirejs, RequireJS.require, RequireJS.define));
