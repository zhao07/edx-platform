(function (undefined) {
    describe('VideoQualityControl', function () {
        var state, oldOTBD;

        beforeEach(function () {
            oldOTBD = window.onTouchBasedDevice;
            window.onTouchBasedDevice = jasmine
                .createSpy('onTouchBasedDevice')
                .andReturn(null);
        });

        afterEach(function () {
            $('source').remove();
            window.onTouchBasedDevice = oldOTBD;
            state.storage.clear();
        });

        describe('constructor', function () {
            beforeEach(function () {
                state = jasmine.initializePlayer('video.html');
            });

            it('render the quality control', function () {
                waitsFor(function () {
                    return state.videoControl;
                }, 'videoControl is present', 5000);

                runs(function () {
                    var container = state.videoControl.secondaryControlsEl;

                    expect(container).toContain('a.quality-control');
                });
            });

            it('add ARIA attributes to quality control', function () {
                var qualityControl = $('a.quality-control');

                expect(qualityControl).toHaveAttrs({
                    'role': 'button',
                    'title': 'HD off',
                    'aria-disabled': 'false'
                });
            });

            it('bind the quality control', function () {
                var handler = state.videoQualityControl.toggleQuality;

                expect($('a.quality-control')).toHandleWith('click', handler);
            });
        });
    });
}).call(this);
