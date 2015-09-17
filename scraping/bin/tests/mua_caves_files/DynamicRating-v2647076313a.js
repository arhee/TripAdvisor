// code ripped out of userreview.js...
// until that code can be refactored to use this

/**
 * Renders the rating bubbles the user can mouse over and click to rate.
 *
 * @option size {number} size of rating bubble (Default: 6)
 * @option prefix {string} className prefix (Default: 's')
 * @option values {object} map of rating to className (Default: {0: '00', 1: '10', ...})
 * @option prefixes {object} map of rating to prefix (Default: {})
 * @option update {element} form element to update with rating when selected
 * @option textNode {element} element to update with rating description from 'strings'
 * @option strings {object} map of rating to text description
 * @option attributeNode {element} element to show when rating is selected
 * @option ratingNode {element} element to add ratingNodeClass to when rating is selected
 * @option ratingNodeClass {string} class to add to ratingNode
 *
 * @class DynamicRating
 */
ta.widgets.DynamicRating = new Class({
  Implements: [Options, Events],
  Binds: ['enter', 'leave', 'move', 'select'],
  options: {
    size: 6,
    prefix: 's',
    values: {
      0: '00',
      1: '10',
      2: '20',
      3: '30',
      4: '40',
      5: '50'
    },
    prefixes: {},
    update: null,
    textNode: false,
    strings: null,
    attributeNode: false,
    ratingNode: false,
    ratingNodeClass: false
  },

  /**
   * @param elmt the visual rating control
   * @param options options, see below
   */
  initialize: function(elmt, options) {
    this.setOptions(options);
    this.src = elmt;
    this.src.addEvent('mouseenter', this.enter);
    this.src.addEvent('mouseleave', this.leave);
    this.src.addEvent('click', this.select);

    // find current class
    this.current = -1;
    for (var i = 0; i <= this.options.size && this.current < 0; i++) {
      if (this.src.hasClass(this.classFor(i))) this.current = i;
    }
    this.selected = this.current;


    this.enter();
  },

  /**
   * @private
   * Return the class to render the rating bubble for the given rating
   * @param i {number} the rating
   * @return {string} the className
   */
  classFor: function(i) {
    return [this.options.prefixes[i], this.options.prefix].pick() + this.options.values[i];
  },

  getIndexForPosition: function(pos) {
    var x = Math.max(pos - this.offsets.left, 1);
    x = Math.ceil(x / this.per);
    x = Math.min(x, 5);
    return ta.util.i18n.isRtl()?6-x:x;  // correct for RTL locale
  },

  enter: function(e) {
    // calculate edge bounds
    this.width = this.src.getSize().x;
    this.per = Math.round(this.width / 5);
    this.src.addEvent('mousemove', this.move);
    this.offsets = this.src.getCoordinates();
    if (e) {
      this.show(this.getIndexForPosition(e.page.x));
    }
  },

  leave: function(e) {
    this.src.removeEvent('mousemove', this.move);
    this.show(this.selected);
    if (this.selected <= 0 && this.options.ratingNode && this.options.ratingNodeClass) {
      this.options.ratingNode.addClass(this.options.ratingNodeClass);
    }
  },

  move: function(e) {
    this.show(this.getIndexForPosition(e.page.x));
  },

  show: function(c) {
    if (c > 5) { // Bounds check
      c = 5;
    }
    this.src.removeClass(this.classFor(this.current));
    this.src.addClass(this.classFor(c));
    this.current = c;
    if (this.options.textNode && this.options.strings) {
      this.options.textNode.set('text', this.options.strings[this.current]);
      if (this.options.ratingNode && this.options.ratingNodeClass) {
        this.options.ratingNode.removeClass(this.options.ratingNodeClass);
      }
    }
  },

  select: function(e) {
    this.selected = parseFloat(e) == e ? e : this.getIndexForPosition(e.page.x);

    if (this.options.update) {
      this.options.update.value = this.selected;
    }
    if (this.options.attributeNode) {
      this.options.attributeNode.show();
    }
    this.fireEvent('onSelect', [this.src, this.selected]);
  }
});

ta.widgets.rating = {};
ta.widgets.rating.factory = {
  create: function(event, elem, locId, type, onSel) {
    event.stop();
    elem.removePropertyEvent('mouseover', 'ta.widgets.rating.factory.create');
    var rating = new ta.widgets.DynamicRating(elem, {
      prefix: 's',
      onSelect: ta.fn(onSel).partial(locId, type)
    });
  }
};
