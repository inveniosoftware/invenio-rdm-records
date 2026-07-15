/*
 * SPDX-FileCopyrightText: 2020-2026 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-FileCopyrightText: 2022 TU Wien.
 * SPDX-License-Identifier: MIT
 */

import { useFormikContext } from "formik";
import {
  Button,
  Header,
  Checkbox,
  Grid,
  Icon,
  Label,
  List,
  Popup,
} from "semantic-ui-react";
import { humanReadableBytes } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import Overridable from "react-overridable";

// NOTE: This component has to be a function component to allow
//       the `useFormikContext` hook.
export const FileUploaderToolbar = (props) => {
  props = {
    ...props,
    filesList: typeof props.filesList === "undefined" ? undefined : props.filesList,
    filesSize: typeof props.filesSize === "undefined" ? undefined : props.filesSize,
    quota: typeof props.quota === "undefined" ? undefined : props.quota,
    decimalSizeDisplay: typeof props.decimalSizeDisplay === "undefined" ? false : props.decimalSizeDisplay,
    showMetadataOnlyToggle:
      typeof props.showMetadataOnlyToggle === "undefined" ? true
        : props.showMetadataOnlyToggle
  };

  const {
    filesList,
    filesSize,
    filesEnabled,
    showMetadataOnlyToggle,
    quota,
    decimalSizeDisplay,
    additionalQuota,
    toggleQuotaSection,
  } = props;
  const { setFieldValue } = useFormikContext();

  const handleOnChangeMetadataOnly = () => {
    setFieldValue("files.enabled", !filesEnabled);
    setFieldValue("access.files", "public");
  };

  return (
    <Overridable
      id="InvenioRdmRecords.DepositForm.FileUploaderToolbar.Container"
      filesList={filesList}
      filesSize={filesSize}
      filesEnabled={filesEnabled}
      showMetadataOnlyToggle={showMetadataOnlyToggle}
      quota={quota}
      decimalSizeDisplay={decimalSizeDisplay}
      handleOnChangeMetadataOnly={handleOnChangeMetadataOnly}
    >
      <>
        <Grid.Column verticalAlign="middle" mobile={16} tablet={4} computer={4}>
          <Overridable
            id="InvenioRdmRecords.DepositForm.FileUploaderToolbar.MetadataOnlyToggle"
            filesList={filesList}
            filesEnabled={filesEnabled}
            showMetadataOnlyToggle={showMetadataOnlyToggle}
            handleOnChangeMetadataOnly={handleOnChangeMetadataOnly}
          >
            {showMetadataOnlyToggle && (
              <List horizontal>
                <List.Item>
                  <Checkbox
                    label={i18next.t("Metadata-only record")}
                    onChange={handleOnChangeMetadataOnly}
                    disabled={filesList.length > 0}
                    checked={!filesEnabled}
                  />
                </List.Item>
                <List.Item className="ml-5">
                  <Popup
                    trigger={
                      <Icon name="question circle outline" className="neutral" />
                    }
                    content={i18next.t("Disable files for this record")}
                    position="top center"
                  />
                </List.Item>
              </List>
            )}
          </Overridable>
        </Grid.Column>
        <Overridable
          id="ReactInvenioDeposit.FileUploaderToolbar.FileList.container"
          filesList={filesList}
          filesSize={filesSize}
          filesEnabled={filesEnabled}
          quota={quota}
          decimalSizeDisplay={decimalSizeDisplay}
        >
          {filesEnabled && (
            <Grid.Column mobile={16} tablet={12} computer={12} className="storage-col">
              <Header size="tiny" className="mr-10">
                {i18next.t("Storage available")}
              </Header>
              <List horizontal floated="right">
                <List.Item>
                  <Label
                    {...(filesList.length === quota.maxFiles ? { color: "blue" } : {})}
                  >
                    {i18next.t(`{{length}} out of {{maxfiles}} files`, {
                      length: filesList.length,
                      maxfiles: quota.maxFiles,
                    })}
                  </Label>
                </List.Item>
                <List.Item>
                  <Label
                    {...(humanReadableBytes(filesSize, decimalSizeDisplay) ===
                    humanReadableBytes(quota.maxStorage, decimalSizeDisplay)
                      ? { color: "blue" }
                      : {})}
                  >
                    {humanReadableBytes(filesSize, decimalSizeDisplay)}{" "}
                    {i18next.t("out of")}{" "}
                    {quota.quotaIncrease?.enabled && quota.quotaIncrease?.valid_user
                      ? humanReadableBytes(
                          quota.quotaIncrease.defaultStorage +
                            additionalQuota * Math.pow(10, 9),
                          decimalSizeDisplay
                        )
                      : humanReadableBytes(quota.maxStorage, decimalSizeDisplay)}
                  </Label>
                </List.Item>
                {quota.quotaIncrease?.enabled && quota.quotaIncrease?.valid_user && (
                  <List.Item>
                    <Button
                      type="button"
                      size="tiny"
                      compact
                      labelPosition="left"
                      icon="cog"
                      content={i18next.t("Manage storage")}
                      onClick={() => {
                        toggleQuotaSection();
                      }}
                    />
                  </List.Item>
                )}
              </List>
            </Grid.Column>
          )}
        </Overridable>
      </>
    </Overridable>
  );
};

FileUploaderToolbar.propTypes = {
  filesList: PropTypes.array,
  filesSize: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  filesEnabled: PropTypes.bool.isRequired,
  quota: PropTypes.object,
  decimalSizeDisplay: PropTypes.bool,
  showMetadataOnlyToggle: PropTypes.bool,
  additionalQuota: PropTypes.number.isRequired,
  toggleQuotaSection: PropTypes.func.isRequired,
};

