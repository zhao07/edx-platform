require(["domReady", "jquery", "underscore", "gettext", "js/views/feedback_notification", "js/views/feedback_prompt",
    "js/utils/get_date", "js/utils/module", "js/utils/handle_iframe_binding", "jquery.ui", "jquery.leanModal", "jquery.form", "jquery.smoothScroll"],
    function(domReady, $, _, gettext, NotificationView, PromptView, DateUtils, ModuleUtils, IframeUtils) {

var $body;
var $newComponentItem;
var $changedInput;
var $spinner;
var $newComponentTypePicker;
var $newComponentTemplatePickers;
var $newComponentButton;

domReady(function() {
    $body = $('body');

    $newComponentItem = $('.new-component-item');
    $newComponentTypePicker = $('.new-component');
    $newComponentTemplatePickers = $('.new-component-templates');
    $newComponentButton = $('.new-component-button');
    $spinner = $('<span class="spinner-in-field-icon"></span>');

    $body.on('click', '.embeddable-xml-input', function() {
        $(this).select();
    });

    $('body').addClass('js');

    $('.unit .item-actions .delete-unit-button').bind('click', deleteUnit);
    $('.new-unit-item').bind('click', createNewUnit);

    // lean/simple modal
    $('a[rel*=modal]').leanModal({
        overlay: 0.80,
        closeButton: '.action-modal-close'
    });
    $('a.action-modal-close').click(function(e) {
        (e).preventDefault();
    });

    // alerts/notifications - manual close
    $('.action-alert-close, .alert.has-actions .nav-actions a').bind('click', hideAlert);
    $('.action-notification-close').bind('click', hideNotification);

    // nav - dropdown related
    $body.click(function(e) {
        $('.nav-dd .nav-item .wrapper-nav-sub').removeClass('is-shown');
        $('.nav-dd .nav-item .title').removeClass('is-selected');
    });

    $('.nav-dd .nav-item').click(function(e) {

        $subnav = $(this).find('.wrapper-nav-sub');
        $title = $(this).find('.title');

        if ($subnav.hasClass('is-shown')) {
            $subnav.removeClass('is-shown');
            $title.removeClass('is-selected');
        } else {
            $('.nav-dd .nav-item .title').removeClass('is-selected');
            $('.nav-dd .nav-item .wrapper-nav-sub').removeClass('is-shown');
            $title.addClass('is-selected');
            $subnav.addClass('is-shown');
            // if propagation is not stopped, the event will bubble up to the
            // body element, which will close the dropdown.
            e.stopPropagation();
        }
    });

    // general link management - new window/tab
    $('a[rel="external"]').attr('title', gettext('This link will open in a new browser window/tab')).bind('click', linkNewWindow);

    // general link management - lean modal window
    $('a[rel="modal"]').attr('title', gettext('This link will open in a modal window')).leanModal({
        overlay: 0.50,
        closeButton: '.action-modal-close'
    });
    $('.action-modal-close').click(function(e) {
        (e).preventDefault();
    });

    // general link management - smooth scrolling page links
    $('a[rel*="view"][href^="#"]').bind('click', smoothScrollLink);

    // tender feedback window scrolling
    $('a.show-tender').bind('click', smoothScrollTop);

    // autosave when leaving input field
    $body.on('change', '.subsection-display-name-input', saveSubsection);
    $('.subsection-display-name-input').each(function() {
        this.val = $(this).val();
    });
    $("#start_date, #start_time, #due_date, #due_time").bind('change', autosaveInput);
    $('.sync-date, .remove-date').bind('click', autosaveInput);

    // expand/collapse methods for optional date setters
    $('.set-date').bind('click', showDateSetter);
    $('.remove-date').bind('click', removeDateSetter);

    $('.delete-section-button').bind('click', deleteSection);
    $('.delete-subsection-button').bind('click', deleteSubsection);

//    $('.unit-status-change-section').bind('click', unitStatusChangeSection);
//    $('.unit-status-change-subsection').bind('click', unitStatusChangeSubsection);
//    $('.unit-status-change-unit').bind('click', unitStatusChangeUnit);

    $('.sync-date').bind('click', syncReleaseDate);

    // section date setting
    $('.set-publish-date').bind('click', setSectionScheduleDate);
    $('.edit-section-start-cancel').bind('click', cancelSetSectionScheduleDate);

    $body.on('change', '.edit-subsection-publish-settings .start-date', function() {
        if ($('.edit-subsection-publish-settings').find('.start-time').val() == '') {
            $('.edit-subsection-publish-settings').find('.start-time').val('12:00am');
        }
    });
    $('.edit-subsection-publish-settings').on('change', '.start-date, .start-time', function() {
        $('.edit-subsection-publish-settings').find('.save-button').show();
    });

    IframeUtils.iframeBinding();
});

function smoothScrollLink(e) {
    (e).preventDefault();

    $.smoothScroll({
        offset: -200,
        easing: 'swing',
        speed: 1000,
        scrollElement: null,
        scrollTarget: $(this).attr('href')
    });
}

function smoothScrollTop(e) {
    (e).preventDefault();

    $.smoothScroll({
        offset: -200,
        easing: 'swing',
        speed: 1000,
        scrollElement: null,
        scrollTarget: $('#view-top')
    });
}

function linkNewWindow(e) {
    window.open($(e.target).attr('href'));
    e.preventDefault();
}

function syncReleaseDate(e) {
    e.preventDefault();
    $(this).closest('.notice').hide();
    $("#start_date").val("");
    $("#start_time").val("");
}


function autosaveInput(e) {
    var self = this;
    if (this.saveTimer) {
        clearTimeout(this.saveTimer);
    }

    this.saveTimer = setTimeout(function() {
        $changedInput = $(e.target);
        saveSubsection();
        self.saveTimer = null;
    }, 500);
}

function saveSubsection() {
    // Spinner is no longer used by subsection name, but is still used by date and time pickers on the right.
    if ($changedInput && !$changedInput.hasClass('no-spinner')) {
        $spinner.css({
            'position': 'absolute',
            'top': Math.floor($changedInput.position().top + ($changedInput.outerHeight() / 2) + 3),
            'left': $changedInput.position().left + $changedInput.outerWidth() - 24,
            'margin-top': '-10px'
        });
        $changedInput.after($spinner);
        $spinner.show();
    }

    var locator = $('.subsection-body').data('locator');

    // pull all 'normalized' metadata editable fields on page
    var metadata_fields = $('input[data-metadata-name]');

    var metadata = {};
    for (var i = 0; i < metadata_fields.length; i++) {
        var el = metadata_fields[i];
        metadata[$(el).data("metadata-name")] = el.value;
    }

    // get datetimes for start and due, stick into metadata
    _(["start", "due"]).each(function(name) {

        var datetime = DateUtils(
            document.getElementById(name+"_date"),
            document.getElementById(name+"_time")
        );
        // if datetime is null, we want to set that in metadata anyway;
        // its an indication to the server to clear the datetime in the DB
        metadata[name] = datetime;
    });

    $.ajax({
        url: ModuleUtils.getUpdateUrl(locator),
        type: "PUT",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            'metadata': metadata
        }),
        success: function() {
            $spinner.delay(500).fadeOut(150);
            $changedInput = null;
        }
    });
}


function createNewUnit(e) {
    e.preventDefault();

    var parent = $(this).data('parent');
    var category = $(this).data('category');

    analytics.track('Created a Unit', {
        'course': course_location_analytics,
        'parent_locator': parent
    });


    $.postJSON(ModuleUtils.getUpdateUrl(), {
        'parent_locator': parent,
        'category': category,
        'display_name': 'New Unit'
    },

    function(data) {
        // redirect to the edit page
        window.location = "/unit/" + data['locator'];
    });
}

function deleteUnit(e) {
    e.preventDefault();
    _deleteItem($(this).parents('li.courseware-unit'), 'Unit');
}

function deleteSubsection(e) {
    e.preventDefault();
    _deleteItem($(this).parents('li.courseware-subsection'), 'Subsection');
}

function deleteSection(e) {
    e.preventDefault();
    _deleteItem($(this).parents('section.courseware-section'), 'Section');
}

function _deleteItem($el, type) {
    var confirm = new PromptView.Warning({
        title: gettext('Delete this ' + type + '?'),
        message: gettext('Deleting this ' + type + ' is permanent and cannot be undone.'),
        actions: {
            primary: {
                text: gettext('Yes, delete this ' + type),
                click: function(view) {
                    view.hide();

                    var locator = $el.data('locator');

                    analytics.track('Deleted an Item', {
                        'course': course_location_analytics,
                        'id': locator
                    });

                    var deleting = new NotificationView.Mini({
                        title: gettext('Deleting&hellip;')
                    });
                    deleting.show();

                    $.ajax({
                        type: 'DELETE',
                        url: ModuleUtils.getUpdateUrl(locator) +'?'+ $.param({recurse: true, all_versions: true}),
                        success: function () {
                            $el.remove();
                            deleting.hide();
                        }
                    });
                }
            },
            secondary: {
                text: gettext('Cancel'),
                click: function(view) {
                    view.hide();
                }
            }
        }
    });
    confirm.show();
}

function showDateSetter(e) {
    e.preventDefault();
    var $block = $(this).closest('.due-date-input');
    $(this).hide();
    $block.find('.date-setter').show();
}

function removeDateSetter(e) {
    e.preventDefault();
    var $block = $(this).closest('.due-date-input');
    $block.find('.date-setter').hide();
    $block.find('.set-date').show();
    // clear out the values
    $block.find('.date').val('');
    $block.find('.time').val('');
}

function hideNotification(e) {
    (e).preventDefault();
    $(this).closest('.wrapper-notification').removeClass('is-shown').addClass('is-hiding').attr('aria-hidden', 'true');
}

function hideAlert(e) {
    (e).preventDefault();
    $(this).closest('.wrapper-alert').removeClass('is-shown');
}

function setSectionScheduleDate(e) {
    e.preventDefault();
    $(this).closest("h4").hide();
    $(this).parent().siblings(".datepair").show();
}

function cancelSetSectionScheduleDate(e) {
    e.preventDefault();
    $(this).closest(".datepair").hide();
    $(this).parent().siblings("h4").show();
}

    window.deleteSection = deleteSection;

//
////________________________________________________ Unit Status Change
////
//
//function unitStatusChangeSection(e) {
//    e.preventDefault();
//    _unitStatusChange($(this).parents('section-item '), 'Section');
//}
//
//function unitStatusChangeSubsection(e) {
//    e.preventDefault();
//    _unitStatusChange($(this).parents('courseware-subsection'), 'Subsection');
//}
//
//function unitStatusChangeUnit(e) {
//    e.preventDefault();
//    _unitStatusChange($(this).parents('li.courseware-unit'), 'Unit');
//}
//
//function _unitStatusChange($el, type) {
//    var public_count = 0;
//    var private_count = 0;
//    var draft_count = 0;
//    var unit_locator_list = '';
//    var action = "make_public";
//
//    for(var i = 0; i < $el.context.children.length; i++) {
//        childElement = $el.context.children[i];
//
//        if(childElement.className == "public_count") {
//           public_count = parseInt(childElement.textContent);
//        }
//        if(childElement.className == "private_count") {
//           private_count = parseInt(childElement.textContent);
//        }
//        if(childElement.className == "draft_count") {
//           draft_count = parseInt(childElement.textContent);
//        }
//        if(childElement.className == "unit_locator_list") {
//           unit_locator_list = childElement.textContent;
//        }
//    }
//
//    if(draft_count > 0) {                   // if there are any units with 'draft' status
//        var messageText = ' unit is ';
//        if(draft_count > 1) {
//            messageText = "  units are "
//        }
//        messageText += 'in "draft" mode, disallowing bulk status updating.'
//        messageText = draft_count.toString() + gettext(messageText);
//        var draftWarning = new PromptView.Warning({
//            title: 'Bulk status update is not allowed',
//            message: messageText,
//            actions: {
//                primary: {
//                    text: gettext('OK'),
//                    click: function(view) {
//                        view.hide();
//                    }
//                }
//            }
//        });
//        draftWarning.show();
//    }
//    else {                                  // else there are no units with 'draft' status
//        var buttonText = gettext("PUBLIC");
//        var promptText =
//            'This section has a mix of {public_count} public and {private_count} private units. Change them all to public?';
//
//        if((public_count > 0) && (private_count == 0))  {
//            if(public_count == 1) {
//                promptText = 'Change {public_count} unit to private?';
//            }
//            else {
//                promptText = 'Change {public_count} units to private?';
//            }
//            buttonText = gettext("PRIVATE");
//            action = "make_private";
//        }
//
//        if((public_count == 0) && (private_count > 0))  {
//            if(private_count == 1) {
//                promptText = 'Change {private_count} unit to public?';
//            }
//            else {
//                promptText = 'Change {private_count} units to public?';
//            }
//            action = "make_public";
//        }
//
//        var translatedText = gettext(promptText);       // translate the static string (before substitution)
//        translatedText = translatedText.replace('{public_count}', public_count.toString())
//        translatedText = translatedText.replace('{private_count}', private_count.toString())
//
//        var confirm = new PromptView.Warning({
//            title: gettext('Change Unit Status (') + type + ')',
//            message: translatedText,
//            actions: {
//                primary: {
//                    text: gettext('Yes, change to ' + buttonText),
//                    click: function(view) {
//                        view.hide();
//                        var updating = new NotificationView.Mini({
//                            title: gettext('Updating&hellip;')
//                        });
//                        updating.show();
//                        changeUnitVisibilityStatus(action, unit_locator_list);
////                        location.reload(true);   // refresh the page
//                    }
//                },
//                secondary: {
//                    text: gettext('Cancel'),
//                    click: function(view) {
//                        view.hide();
//                    }
//                }
//            }
//        });
//        confirm.show();
//    }
//}
//
//function changeUnitVisibilityStatus( action, unit_locator_list ) {
//    unit_locator_array = unit_locator_list.split(";");
//    for(i=0; i<unit_locator_array.length; i++) {
//        var clean_locator = unit_locator_array[i].trim();
//        if(clean_locator.length > 0) {
//            var xblockURL = "/xblock/" + clean_locator;
//            $.postJSON(xblockURL, {publish: action} );   // issue a change message to each unit
//        }
//    }
//}
//
//
//
//
//
//
//
//
//
//
//
//
//
//
}); // end require()
