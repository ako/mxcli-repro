# Gallery

- **Widget ID:** `com.mendix.widget.web.gallery.Gallery`
- **Type:** PLUGGABLEWIDGET
- **Version:** 3.0.1

## MDL Example

```sql
PLUGGABLEWIDGET 'com.mendix.widget.web.gallery.Gallery' widget1
```

## Properties

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `filtersPlaceholder` | widgets |  |  |  |
| `datasource` | datasource | Yes |  |  |
| `itemSelection` | selection | Yes |  |  |
| `itemSelectionMode` | enumeration | Yes | clear | Defines item selection behavior. |
| `content` | widgets |  |  |  |
| `desktopItems` | integer | Yes | 1 |  |
| `tabletItems` | integer | Yes | 1 |  |
| `phoneItems` | integer | Yes | 1 |  |
| `pageSize` | integer | Yes | 20 |  |
| `pagination` | enumeration | Yes | buttons |  |
| `pagingPosition` | enumeration | Yes | below |  |
| `showPagingButtons` | enumeration | Yes | always |  |
| `showTotalCount` | boolean | Yes | false |  |
| `showEmptyPlaceholder` | enumeration | Yes | none |  |
| `emptyPlaceholder` | widgets |  |  |  |
| `itemClass` | expression |  |  |  |
| `onClickTrigger` | enumeration | Yes | single |  |
| `onClick` | action |  |  |  |
| `onSelectionChange` | action |  |  |  |
| `filterSectionTitle` | textTemplate |  |  | Assistive technology will read this upon reaching a filtering or sorting sect... |
| `emptyMessageTitle` | textTemplate |  |  | Assistive technology will read this upon reaching an empty message section. |
| `ariaLabelListBox` | textTemplate |  |  | Assistive technology will read this upon reaching gallery. |
| `ariaLabelItem` | textTemplate |  |  | Assistive technology will read this upon reaching each gallery item. |

