/**
 * This is a base modal implementation that provides common utilities.
 */
define(["jquery", "underscore", "js/views/baseview"],
    function($, _, BaseView) {
        var BaseModal = BaseView.extend({
            events : {
                "click .action-cancel": "cancel"
            },

            options: $.extend({}, BaseView.prototype.options, {
                type: "prompt",
                closeIcon: false,
                icon: false,
                modalName: 'basic',
                modalType: 'generic',
                modalSize: 'lg',
                title: ""
            }),

            initialize: function() {
                var parent = this.options.parent,
                    parentElement = this.options.parentElement;
                this.modalTemplate = _.template($("#basic-modal-tpl").text());
                if (parent) {
                    parentElement = parent.$el;
                } else if (!parentElement) {
                    parentElement = this.$el.closest('.modal-window');
                    if (parentElement.length === 0) {
                        parentElement = $('body');
                    }
                }
                this.parentElement = parentElement;
            },

            render: function() {
                var contentHtml = this.getContentHtml(),
                    parentElement;
                this.$el.html(this.modalTemplate({
                    name: this.options.modalName,
                    type: this.options.modalType,
                    size: this.options.modalSize,
                    title: this.options.title
                }));
                this.$('.modal-content').html(contentHtml);
                this.parentElement.append(this.$el);
            },

            /**
             * Returns the content to be shown in the modal.
             */
            getContentHtml: function() {
                return "";
            },

            show: function() {
                this.render();
                this.center();
                this.lastPosition = $(document).scrollTop();
            },

            hide: function() {
                $(document).scrollTop(this.lastPosition);

                // Completely remove the modal from the DOM
                this.undelegateEvents();
                this.$el.html('');
            },

            cancel: function(event) {
                event.preventDefault();
                event.stopPropagation(); // Make sure parent modals don't see the click
                this.hide();
            },

            center: function () {
                var top, left, modalWindow;

                modalWindow = this.$('.modal-window');

                top = Math.max($(window).height() - modalWindow.outerHeight(), 0) / 2;
                left = Math.max($(window).width() - modalWindow.outerWidth(), 0) / 2;

                modalWindow.css({
                    top: top + $(window).scrollTop(),
                    left: left + $(window).scrollLeft()
                });
            }
        });

        return BaseModal;
    });
