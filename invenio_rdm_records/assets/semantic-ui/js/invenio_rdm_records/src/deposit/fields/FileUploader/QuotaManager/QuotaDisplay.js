import React from "react";
import PropTypes from "prop-types";
import { Group } from "@visx/group";
import { BarStackHorizontal } from "@visx/shape";
import { scaleBand, scaleLinear, scaleOrdinal } from "@visx/scale";
import { Text } from "@visx/text";
import { Label } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Trans } from "react-i18next";

export const QuotaDisplay = (props) => {
  const { width, height, additionalQuota, quota } = props;
  const { defaultStorage, remainingStorage } = quota;

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
      default: defaultStorage,
      additional: additionalQuota,
      available: remainingStorage - additionalQuota,
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
    domain: [0, defaultStorage + remainingStorage],
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
        <div>{defaultStorage + remainingStorage} GB</div>
      </div>
      {/* Storage Visualization */}
      <div>
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
              <span className="ml-5">
                {i18next.t("Default")} ({defaultStorage}&nbsp;GB)
              </span>
            </div>
            <div className="flex align-items-center ml-10">
              <Label circular color="green" empty key="green" />
              <span className="ml-5">
                {i18next.t("Additional")} (+{additionalQuota}&nbsp;GB)
              </span>
            </div>
            <div className="flex align-items-center ml-10">
              <Label circular color="grey" empty key="grey" />
              <span className="ml-5">
                {i18next.t("Available")} ({remainingStorage - additionalQuota}
                &nbsp;GB)
              </span>
            </div>
          </div>
          <div>
            <Trans>
              See your <a href="/account/settings/quota">storage settings</a> for usage
              across all records
            </Trans>
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
  quota: PropTypes.object.isRequired,
};
