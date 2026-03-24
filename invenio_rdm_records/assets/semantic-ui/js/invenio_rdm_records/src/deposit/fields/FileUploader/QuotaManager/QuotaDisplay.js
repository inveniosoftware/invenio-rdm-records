import React from "react";
import PropTypes from "prop-types";
import { Group } from "@visx/group";
import { BarStackHorizontal } from "@visx/shape";
import { scaleBand, scaleLinear, scaleOrdinal } from "@visx/scale";
import { Text } from "@visx/text";
import { Label } from "semantic-ui-react";

export const QuotaDisplay = (props) => {
  const { width, height, additionalQuota, quota } = props;

  // Colors for the bar segments
  const colors = {
    default: "#2185d0",
    additional: "#048622",
    available: "#767676",
  };

  // Data for the stacked bar chart
  const data = [
    {
      category: "Storage",
      default: quota.defaultStorage,
      additional: additionalQuota,
      available: quota.remainingStorage - additionalQuota,
    },
  ];

  // Accessors
  const keys = ["default", "additional", "available"].filter((key) => data[0][key] > 0);

  // Scales
  const categoryScale = scaleBand({
    domain: ["Storage"],
    padding: 0.2,
  });

  const valueScale = scaleLinear({
    domain: [0, quota.defaultStorage + quota.remainingStorage],
    nice: true,
  });

  const colorScale = scaleOrdinal({
    domain: keys,
    range: keys.map((key) => colors[key]),
  });

  // Update scales with dimensions
  categoryScale.rangeRound([0, height]);
  valueScale.rangeRound([0, width]);

  return (
    <>
      <div className="flex align-items-center justify-space-between">
        <div>0 GB</div>
        <div>{quota.defaultStorage + quota.remainingStorage} GB</div>
      </div>
      {/* Storage Visualization */}
      <div className="mb-25">
        {/* Bar Stack */}
        <svg width={width} height={height}>
          <Group left={0} top={0}>
            <BarStackHorizontal
              data={data}
              keys={keys}
              height={height}
              y={(d) => d.category}
              xScale={valueScale}
              yScale={categoryScale}
              color={colorScale}
            >
              {(barStacks) => {
                return barStacks.map((barStack) =>
                  barStack.bars.map((bar) => (
                    <rect
                      key={`barstack-horizontal-${barStack.index}-${bar.index}`}
                      x={bar.x}
                      y={bar.y}
                      width={bar.width}
                      height={bar.height}
                      fill={bar.color}
                    />
                  ))
                );
              }}
            </BarStackHorizontal>

            <>
              {keys.map((key, index) => {
                const bar = data[0];
                let xOffset = 0;
                for (let i = 0; i < index; i++) {
                  xOffset += bar[keys[i]];
                }
                const barWidth = bar[key];
                const xPos =
                  valueScale(xOffset) +
                  (barWidth > 15 ? valueScale(barWidth) / 2 : valueScale(barWidth) + 5);

                if (barWidth <= 0) return null;

                return (
                  <Text
                    key={`label-${key}`}
                    x={xPos}
                    y={categoryScale("Storage") + categoryScale.bandwidth() / 2}
                    verticalAnchor="middle"
                    textAnchor={barWidth > 15 ? "middle" : "start"}
                    fontSize={11}
                    fill="white"
                    fontWeight={500}
                  >
                    {`${barWidth} GB`}
                    {/* passing as a single string as otherwise commas are added */}
                  </Text>
                );
              })}
            </>
          </Group>
        </svg>

        {/* Legend */}
        <div className="flex align-items-center justify-space-between">
          <div className="flex">
            <div className="flex align-items-center">
              <Label circular color="blue" empty key="blue" />
              <span className="ml-5">Default ({quota.defaultStorage}&nbsp;GB)</span>
            </div>
            <div className="flex align-items-center ml-10">
              <Label circular color="green" empty key="green" />
              <span className="ml-5">Additional (+{additionalQuota}&nbsp;GB)</span>
            </div>
            <div className="flex align-items-center ml-10">
              <Label circular color="grey" empty key="grey" />
              <span className="ml-5">
                Available ({quota.remainingStorage - additionalQuota}&nbsp;GB)
              </span>
            </div>
          </div>
          <div>
            See your <a href="/">storage settings</a> for usage across all records
          </div>
        </div>
      </div>
    </>
  );
};

QuotaDisplay.propTypes = {
  width: PropTypes.number.isRequired,
  height: PropTypes.number.isRequired,
  additionalQuota: PropTypes.number.isRequired,
  quota: PropTypes.object,
};

QuotaDisplay.defaultProps = {
  quota: {
    maxFiles: 5,
    maxStorage: 10,
    defaultStorage: 10,
    additionalStorage: 0,
    maxAdditionalStorage: 0,
    remainingStorage: 0,
  },
};
