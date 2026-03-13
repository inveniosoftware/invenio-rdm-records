import React from "react";
import { Grid, Button, Icon, Message, Input } from "semantic-ui-react";
import PropTypes from "prop-types";
import { ParentSize } from "@visx/responsive";
import { QuotaDisplay } from "./QuotaDisplay";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export const QuotaManager = (props) => {
  const { toggleQuotaSection, additionalQuota, setAdditionalQuota } = props;
  return (
    <Grid.Column width={16}>
      <Message className="pt-20 pb-20">
        <Grid>
          <Grid.Column width={15} className="pt-0">
            <strong>Manage storage</strong>
          </Grid.Column>
          <Grid.Column width={1} className="pt-0">
            <Icon
              name="close"
              className="right-floated link"
              onClick={() => toggleQuotaSection()}
            />
          </Grid.Column>
        </Grid>
        <Message info>
          Each record has a default quota of 50 GB. You have an additional allowance of
          up to 150GB that can be distributed across your uploads as needed.
        </Message>

        {/* Progress bar */}
        <ParentSize>
          {({ width, height }) => (
            <QuotaDisplay
              width={width}
              height={40}
              defaultQuota={50}
              additionalQuota={additionalQuota}
              maxQuota={200}
            />
          )}
        </ParentSize>

        <div className="flex align-items-center justify-space-between">
          <strong id="additional-storage">{i18next.t("Additional storage")}</strong>

          <Input
            size="small"
            aria-labelledby="additional-storage"
            type="number"
            value={additionalQuota}
            onChange={(e, { k, value }) => setAdditionalQuota(parseInt(value))}
          />
        </div>

        <Input
          value={additionalQuota}
          onChange={(e, { k, value }) => setAdditionalQuota(parseInt(value))}
          min={0}
          max={150}
          name="quota"
          step={1}
          type="range"
          style={{ width: "100%" }}
        />
        <div className="flex align-items-center justify-space-between pb-20">
          <div>0 GB</div>
          <div>New total: {50 + additionalQuota} GB</div>
          <div>150 GB</div>
        </div>
        <div className="flex justify-end">
          <Button
            type="button"
            color="green"
            labelPosition="left"
            icon="check"
            content="Apply"
          />
        </div>
      </Message>
    </Grid.Column>
  );
};

QuotaManager.propTypes = {
  toggleQuotaSection: PropTypes.func.isRequired,
  additionalQuota: PropTypes.number.isRequired,
  setAdditionalQuota: PropTypes.func.isRequired,
};
