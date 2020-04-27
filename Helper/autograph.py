from Facility import DashboardPanel
from .log import LogInfo, Log
from typing import List
import re


class AutoGraph:
    regex = re.compile(r".*AutoGraph: Gr\.(.*) '([^']*)'-'([^']*)'\((.*)\)")

    @classmethod
    def GeneratePanels(cls, existing: List[DashboardPanel], log: LogInfo) -> List[DashboardPanel]:
        matches: List[re.Match] = []
        res: List[DashboardPanel] = []

        for severity, message in log.Log:
            if severity == "Info":
                match = cls.regex.match(message)
                if match:
                    matches.append(match)

        if len(matches) > 0:
            column, row = cls.getLastPos(existing)
            freeSpaces = (24-(row-1)) // 8

            for index in range(freeSpaces):  # First cover the available space in the last row
                if len(matches) > 0:
                    match = matches.pop(0)
                    res.append(cls.generateSinglePanel(match, column + 8 * index, row - 8))

            row += 1  # Then generate new rows for the rest of the panels
            for index, match in enumerate(matches):
                res.append(cls.generateSinglePanel(match, (index % 3) * 8, row + (index // 3)))

        return res

    @staticmethod
    def getLastPos(existing: List[DashboardPanel]):
        maxRow = 0
        maxColumn = 0

        for panel in existing:  # Find the last occupied row
            lastPanelRow = panel.Position[1] + panel.Size[1]
            if lastPanelRow > maxRow:
                maxRow = lastPanelRow

        for panel in existing:  # For the panels in that row, find the last used column
            lastPanelRow = panel.Position[1] + panel.Size[1]
            if lastPanelRow == maxRow:
                lastPanelColumn = panel.Position[0] + panel.Size[0]
                if lastPanelColumn > maxColumn:
                    maxColumn = lastPanelColumn

        return maxColumn, maxRow

    @staticmethod
    def generateSinglePanel(match: re.Match, column: int, row: int) -> DashboardPanel:
        format, table, field, unit = match.groups()

        data = {
            'Name': str(field).split('[[')[0].strip(),
            'Measurement': table,
            'Field': field,
            'Size': [8, 8],
            'Position': [column, row],
            'Interval': '1s'
        }

        if len(unit) > 0:
            data['Unit'] = unit

        if format in ['Single', 'Gauge']:
            data['Type'] = 'singlestat'
            data['Gauge'] = (format == 'Gauge')
            if format == 'Gauge':
                data['Thresholds'] = [0, 25, 75, 100]
        elif format in ['Lines', 'Bars']:
            data['Type'] = 'graph'
            data['Lines'] = (format == 'Lines')

        return DashboardPanel(data)
